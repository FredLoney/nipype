import os

from nipype.testing import *
import nipype.interfaces.fsl as fsl

def test_fslversion():
    ver = fsl.fsl_info.version
    if ver:
        # If ver is None, fsl is not installed
        ver = ver.split('.')
        yield assert_equal, ver[0], '4'

    
def test_fsloutputtype():
    types = ['ANALYZE_GZ', 'NIFTI_PAIR_GZ', 'NIFTI', 'NIFTI_PAIR',
             'NIFTI_GZ', 'ANALYZE']
    out_type, ext = fsl.fsl_info.outputtype()
    if out_type is None:
        # Environment variable is not set.  FSL may not be installed.
        return
    yield assert_true, out_type in types
    env_type = os.environ.get('FSLOUTPUTTYPE')
    if env_type:
        # Set to same value for test.
        out_type, ext = fsl.fsl_info.outputtype(env_type)
        yield assert_equal, out_type, env_type


def test_FSLCommand():
    # Most methods in FSLCommand are tested in the subclasses.  Only
    # testing the one item that is not.
    cmd = fsl.FSLCommand()
    cmd.cmd = 'bet' # Set the cmd to something
    res = cmd.run()
    yield assert_equal, type(res), fsl.InterfaceResult
    

# test Bet
def test_bet():
    better = fsl.Bet()
    yield assert_equal, better.cmd, 'bet'

    # Test raising error with mandatory args absent
    yield assert_raises, ValueError, better.run

    # .inputs based parameter setting
    better.inputs.frac = 0.5
    better.inputs.infile = 'infile'
    better.inputs.outfile = 'outfile'
    yield assert_equal, better.cmdline, 'bet infile '+os.path.realpath('outfile')+' -f 0.50'

    # .run() based parameter setting
    betted = better.run(infile='infile2', outfile='outfile')
    # Non-existant files, shouldn't finish cleanly
    yield assert_not_equal, betted.runtime.returncode, 0
    yield assert_equal, betted.interface.inputs.infile, 'infile2'
    yield assert_equal, betted.interface.inputs.outfile, 'outfile'
    yield assert_equal, betted.runtime.cmdline, 'bet infile2 '+os.path.realpath('outfile')+' -f 0.50'
    
    # test that an outfile is autogenerated when inputs.outfile is None
    better = fsl.Bet()
    better.inputs.infile = 'infile'
    res = better.run()
    outfile = os.path.join(os.path.abspath('.'), 'infile_bet')
    # This behavior is bad, see Trac ticket #42
    # yield assert_equal, better.inputs.outfile, outfile

    # Our options and some test values for them
    # Should parallel the opt_map structure in the class for clarity
    opt_map = {
        'outline':            ('-o', True),
        'mask':               ('-m', True),
        'skull':              ('-s', True),
        'nooutput':           ('-n', True),
        'frac':               ('-f 0.40', 0.4),
        'vertical_gradient':  ('-g 0.75', 0.75),
        'radius':             ('-r 20', 20),
        'center':             ('-c 54 75 80', (54, 75, 80)),
        'threshold':          ('-t', True),
        'mesh':               ('-e', True),
        'verbose':            ('-v', True),
        'flags':              ('--i-made-this-up', '--i-made-this-up'),
            }
    # Currently we don't test -R, -S, -B, -Z, -F, -A or -A2
    

    # test each of our arguments
    for name, settings in opt_map.items():
        better = fsl.Bet(**{name: settings[1]})
        yield assert_equal, better.cmdline, ' '.join([better.cmd, settings[0]])
    
        
# test fast
def test_fast():
    faster = fsl.Fast()
    faster.inputs.verbose = True
    fasted = faster.run(infiles='infile')
    fasted2 = faster.run(infiles=['infile', 'otherfile'])
    
    yield assert_equal, faster.cmd, 'fast'
    yield assert_equal, faster.inputs.verbose, True
    yield assert_equal, faster.inputs.manualseg , None
    yield assert_not_equal, faster, fasted
    yield assert_equal, fasted.runtime.cmdline, 'fast -v infile'
    yield assert_equal, fasted2.runtime.cmdline, 'fast -v infile otherfile'

    faster = fsl.Fast()
    faster.inputs.infiles = 'foo.nii'
    yield assert_equal, faster.cmdline, 'fast foo.nii'
    faster.inputs.infiles = ['foo.nii', 'bar.nii']
    yield assert_equal, faster.cmdline, 'fast foo.nii bar.nii'
    
    # Our options and some test values for them
    # Should parallel the opt_map structure in the class for clarity
    opt_map = {'number_classes':       ('-n 4', 4),
               'bias_iters':           ('-I 5', 5),
               'bias_lowpass':         ('-l 15', 15),
               'img_type':             ('-t 2', 2),
               'init_seg_smooth':      ('-f 0.035', 0.035),
               'segments':             ('-g', True),
               'init_transform':       ('-a xform.mat', 'xform.mat'),
               'other_priors':         ('-A prior1.nii prior2.nii prior3.nii', 
                       ('prior1.nii', 'prior2.nii', 'prior3.nii')),
               'nopve':                ('--nopve', True),
               'output_biasfield':     ('-b', True),
               'output_biascorrected': ('-B', True),
               'nobias':               ('-N', True),
               'n_inputimages':        ('-S 2', 2),
               'out_basename':         ('-o fasted', 'fasted'),
               'use_priors':           ('-P', True),
               'segment_iters':        ('-W 14', 14),
               'mixel_smooth':         ('-R 0.25', 0.25),
               'iters_afterbias':      ('-O 3', 3),
               'hyper':                ('-H 0.15', 0.15),
               'verbose':              ('-v', True), 
               'manualseg':            ('-s intensities.nii',
                       'intensities.nii'),
               'probability_maps':     ('-p', True),
              }
   
    # test each of our arguments
    for name, settings in opt_map.items():
        faster = fsl.Fast(**{name: settings[1]})
        yield assert_equal, faster.cmdline, ' '.join([faster.cmd, settings[0]])


#test flirt
def test_flirt():
    flirter = fsl.Flirt()
    flirter.inputs.bins = 256
    flirter.inputs.cost = 'mutualinfo'
    flirted = flirter.run(infile='infile',reference='reffile',
                          outfile='outfile',outmatrix='outmat.mat')
    flirt_est = flirter.run(infile='infile',reference='reffile',
                            outfile=None,outmatrix='outmat.mat')

    yield assert_not_equal, flirter, flirted
    yield assert_not_equal, flirted, flirt_est

    yield assert_equal, flirter.cmd, 'flirt'
    yield assert_equal, flirter.inputs.bins, flirted.interface.inputs.bins
    yield assert_equal, flirter.inputs.cost, flirt_est.interface.inputs.cost
    yield assert_equal, flirted.runtime.cmdline, \
        'flirt -in infile -ref reffile -omat outmat.mat -out outfile ' \
        '-bins 256 -cost mutualinfo'

    flirter = fsl.Flirt()
    # infile not specified
    yield assert_raises, AttributeError, flirter.run
    flirter.inputs.infile = 'foo.nii'
    # reference not specified
    yield assert_raises, AttributeError, flirter.run
    flirter.inputs.reference = 'mni152.nii'
    res = flirter.run()
    realcmd = 'flirt -in foo.nii -ref mni152.nii'
    yield assert_equal, res.interface.cmdline, realcmd
    inputs = dict(flags='-v')
    res = flirter.run(**inputs)
    realcmd ='flirt -in foo.nii -ref mni152.nii -v'
    yield assert_equal, res.interface.cmdline, realcmd


def test_applyxfm():
    # ApplyXFM subclasses Flirt.
    flt = fsl.ApplyXFM(infile='subj.nii', inmatrix='xfm.mat', 
                       outfile='xfm_subj.nii', reference='mni152.nii')
    flted = flt.run()
    yield assert_equal, flt.cmdline, \
        'flirt -in subj.nii -ref mni152.nii -init xfm.mat ' \
        '-applyxfm -out xfm_subj.nii'
    flt = fsl.ApplyXFM()
    yield assert_raises, AttributeError, flt.run
    flt.inputs.infile = 'subj.nii'
    flt.inputs.outfile = 'xfm_subj.nii'
    # reference not specified
    yield assert_raises, AttributeError, flt.run
    flt.inputs.reference = 'mni152.nii'
    # inmatrix not specified
    yield assert_raises, AttributeError, flt.run
    flt.inputs.inmatrix = 'xfm.mat'
    res = flt.run()
    realcmd = 'flirt -in subj.nii -ref mni152.nii -init xfm.mat '\
        '-applyxfm -out xfm_subj.nii'
    yield assert_equal, res.interface.cmdline, realcmd


# Mcflirt
def test_mcflirt():
    frt = fsl.McFlirt()
    yield assert_equal, frt.cmd, 'mcflirt'
    
    opt_map = {
        'outfile':     ('-out bar.nii', 'bar.nii'),
        'cost':        ('-cost mutualinfo', 'mutualinfo'),
        'bins':        ('-bins 256', 256),
        'dof':         ('-dof 6', 6),
        'refvol':      ('-refvol 2', 2),
        'scaling':     ('-scaling 6.00', 6.00),
        'smooth':      ('-smooth 1.00', 1.00),
        'rotation':    ('-rotation 2', 2),
        'verbose':     ('-verbose', True),
        'stages':      ('-stages 3', 3),
        'init':        ('-init matrix.mat', 'matrix.mat'),
        'usegradient': ('-gdt', True),
        'usecontour':  ('-edge', True),
        'meanvol':     ('-meanvol', True),
        'statsimgs':   ('-stats', True),
        'savemats':    ('-mats', True),
        'saveplots':   ('-plots', True),
        'report':      ('-report', True),
        }

    for name, settings in opt_map.items():
        fnt = fsl.McFlirt(**{name : settings[1]})
        yield assert_equal, fnt.cmdline, ' '.join([fnt.cmd, settings[0]])

    # Test error is raised when missing required args
    fnt = fsl.McFlirt()
    yield assert_raises, AttributeError, fnt.run
    # Test run result
    fnt = fsl.McFlirt()
    fnt.inputs.infile = 'foo.nii'
    res = fnt.run()
    yield assert_equal, type(res), fsl.InterfaceResult
    res = fnt.run(infile='bar.nii')
    yield assert_equal, type(res), fsl.InterfaceResult


#test fnirt
def test_fnirt():
    fnirt = fsl.Fnirt()
    yield assert_equal, fnirt.cmd, 'fnirt'

    # Test inputs with variable number of values
    fnirt.inputs.sub_sampling = [8,6,4]
    yield assert_equal, fnirt.inputs.sub_sampling, [8,6,4]
    fnirtd = fnirt.run(infile='infile', reference='reference')
    realcmd = 'fnirt --in=infile --ref=reference --subsamp=8,6,4'
    yield assert_equal, fnirtd.runtime.cmdline, realcmd

    fnirt2 = fsl.Fnirt(sub_sampling=[8,2])
    fnirtd2 = fnirt2.run(infile='infile', reference='reference')
    realcmd = 'fnirt --in=infile --ref=reference --subsamp=8,2'
    yield assert_equal, fnirtd2.runtime.cmdline, realcmd

    # Test case where input that can be a list is just a single value
    params = [('sub_sampling', '--subsamp'),
              ('max_iter', '--miter'),
              ('referencefwhm', '--reffwhm'),
              ('imgfwhm', '--infwhm'),
              ('lambdas', '--lambda'),
              ('estintensity', '--estint'),
              ('applyrefmask', '--applyrefmask'),
              ('applyimgmask', '--applyinmask')]
    for item, flag in params:
        
        
        if item in ('sub_sampling', 'max_iter',
                    'referencefwhm', 'imgfwhm',
                    'lambdas', 'estintensity'):
            fnirt = fsl.Fnirt(**{item : 5})
            cmd = 'fnirt %s=%d' % (flag, 5)
        else:
            fnirt = fsl.Fnirt(**{item : 5})
            cmd = 'fnirt %s=%f' % (flag, 5)
        yield assert_equal, fnirt.cmdline, cmd

    # Test error is raised when missing required args
    fnirt = fsl.Fnirt()
    yield assert_raises, AttributeError, fnirt.run
    fnirt.inputs.infile = 'foo.nii'
    # I don't think this is correct. See Fnirt documentation -DJC
    # yield assert_raises, AttributeError, fnirt.run
    fnirt.inputs.reference = 'mni152.nii'
    res = fnirt.run()
    yield assert_equal, type(res), fsl.InterfaceResult

    opt_map = {
        'affine':           ('--aff=affine.mat', 'affine.mat'),
        'initwarp':         ('--inwarp=warp.mat', 'warp.mat'),
        'initintensity':    ('--intin=inten.mat', 'inten.mat'),
        'configfile':       ('--config=conf.txt', 'conf.txt'),
        'referencemask':    ('--refmask=ref.mat', 'ref.mat'),
        'imagemask':        ('--inmask=mask.nii', 'mask.nii'),
        'fieldcoeff_file':  ('--cout=coef.txt', 'coef.txt'),
        'outimage':         ('--iout=out.nii', 'out.nii'),
        'fieldfile':        ('--fout=fld.txt', 'fld.txt'),
        'jacobianfile':     ('--jout=jaco.txt', 'jaco.txt'),
        'reffile':          ('--refout=refout.nii', 'refout.nii'),
        'intensityfile':    ('--intout=intout.txt', 'intout.txt'),
        'logfile':          ('--logout=log.txt', 'log.txt'),
        'verbose':          ('--verbose', True),
        'flags':            ('--fake-flag', '--fake-flag')}

    for name, settings in opt_map.items():
        fnirt = fsl.Fnirt(**{name : settings[1]})
        yield assert_equal, fnirt.cmdline, ' '.join([fnirt.cmd, settings[0]])




# nosetests --with-doctest path_to/test_fsl.py
#----------------------------------------------------------------------------------------------------------------

# test bedpostx
def test_bedpostx():
    bpx = fsl.Bedpostx()

    # make sure command gets called
    yield assert_equal, bpx.cmd, 'bedpostx'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, bpx.run    
    
    # .inputs based parameters setting
    bpx2 = fsl.Bedpostx()
    bpx2.inputs.directory = 'inputDir'
    bpx2.inputs.fibres = 2
    bpx2.inputs.weight = 0.3
    bpx2.inputs.burn_period = 200
    bpx2.inputs.jumps = 500
    bpx2.inputs.sampling = 20    
    actualCmdline = sorted(bpx2.cmdline.split())
    cmd = 'bedpostx inputDir -w 0.30 -n 2 -j 500 -b 200 -s 20'
    desiredCmdline = sorted(cmd.split())    
    yield assert_equal, actualCmdline, desiredCmdline
          

    # .run based parameter setting
    bpx3 = fsl.Bedpostx(fibres=1,directory='inputDir')
    yield assert_equal, bpx3.cmdline, 'bedpostx inputDir -n 1'

    results=bpx3.run(fibres=1,directory='inputDir',noseTest=True)
    yield assert_not_equal, results.runtime.returncode, 0
    yield assert_equal, results.interface.inputs.fibres, 1
    yield assert_equal, results.interface.inputs.directory, 'inputDir'
    yield assert_equal, results.runtime.cmdline, 'bedpostx inputDir -n 1'
    
    # test arguments for opt_map
    opt_map = {
                'fibres':               ('-n 1', 1),
                'weight':               ('-w 1.00',1.0),
                'burn_period':          ('-b 1000',1000),
                'jumps':                ('-j 1250',1250), 
                'sampling':             ('-s 25',25)}

    for name, settings in opt_map.items():
        bpx4 = fsl.Bedpostx(directory='inputDir',**{name: settings[1]})
        yield assert_equal, bpx4.cmdline, bpx4.cmd+' inputDir '+settings[0]

    
# test eddy_correct
def test_eddy_correct():
    eddy = fsl.Eddy_correct()

    # make sure command gets called
    yield assert_equal, eddy.cmd, 'eddy_correct'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, eddy.run 

    # .inputs based parameters setting
    eddy.inputs.infile='foo.nii'
    eddy.inputs.outfile='foo_eddc.nii'
    eddy.inputs.reference_vol=100
    yield assert_equal, eddy.cmdline, 'eddy_correct foo.nii foo_eddc.nii 100'

    # .run based parameter setting
    eddy2 = fsl.Eddy_correct(infile='foo',outfile='foo_eddc',reference_vol=20)
    yield assert_equal, eddy2.cmdline, 'eddy_correct foo foo_eddc 20'

    eddy3 = fsl.Eddy_correct()
    results=eddy3.run(infile='foo',outfile='foo_eddc',reference_vol=10)
    yield assert_equal, results.interface.inputs.infile, 'foo'
    yield assert_equal, results.interface.inputs.outfile, 'foo_eddc'
    yield assert_equal, results.runtime.cmdline, 'eddy_correct foo foo_eddc 10'

    # test arguments for opt_map
    # eddy_correct class doesn't have opt_map{}
    
    
# test dtifit  
def test_dtifit():
    dti=fsl.Dtifit()
    
    # make sure command gets called
    yield assert_equal, dti.cmd, 'dtifit'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, dti.run 

    # .inputs based parameters setting
    dti.inputs.data='foo.nii'
    dti.inputs.basename='foo.dti.nii'
    dti.inputs.bet_binary_mask='nodif_brain_mask'
    dti.inputs.min_z = 10
    dti.inputs.max_z = 50
    
    actualCmdline = sorted(dti.cmdline.split())
    cmd = 'dtifit -k foo.nii -o foo.dti.nii -m nodif_brain_mask -z 10 -Z 50'
    desiredCmdline = sorted(cmd.split())    
    yield assert_equal, actualCmdline, desiredCmdline

    # .run based parameter setting
    dti2 = fsl.Dtifit(data='foo2.nii')
    yield assert_equal, dti2.cmdline, 'dtifit -k foo2.nii'

    dti3 = fsl.Dtifit()
    results=dti3.run(data='foo3.nii',noseTest=True)
    yield assert_not_equal, results.runtime.returncode, 0
    yield assert_equal, results.interface.inputs.data, 'foo3.nii'
    yield assert_equal, results.runtime.cmdline, 'dtifit -k foo3.nii'

    # test arguments for opt_map
    opt_map = {
                'data':                     ('-k subj1', 'subj1'),
                'basename':                 ('-o subj1', 'subj1'),
                'bet_binary_mask':          ('-m nodif_brain_mask','nodif_brain_mask'),
                'b_vector_file':            ('-r bvecs','bvecs'), 
                'b_value_file':             ('-b bvals','bvals'),
                'min_z':                    ('-z 10', 10),
                'max_z':                    ('-Z 20', 20),
                'min_y':                    ('-y 10', 10),
                'max_y':                    ('-Y 30', 30),
                'min_x':                    ('-x 5', 5),
                'max_x':                    ('-X 50', 50),
                'verbose':                  ('-V', True),
                'save_tensor':              ('--save_tensor', True),
                'sum_squared_errors':       ('--sse', True),
                'inp_confound_reg':         ('--cni', True),
                'small_brain_area':         ('--littlebit', True)}

    for name, settings in opt_map.items():
        dti4 = fsl.Dtifit(**{name: settings[1]})
        yield assert_equal, dti4.cmdline, dti4.cmd+' '+settings[0]

    

def test_fslroi():
    roi = fsl.Fslroi()

    # make sure command gets called
    yield assert_equal, roi.cmd, 'fslroi'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, roi.run 

    # .inputs based parameters setting
    roi.inputs.infile='foo.nii'
    roi.inputs.outfile='foo_roi.nii'
    roi.inputs.tmin=10
    roi.inputs.tsize=20
    yield assert_equal, roi.cmdline, 'fslroi foo.nii foo_roi.nii 10 20'

    # .run based parameter setting
    roi2 = fsl.Fslroi(infile='foo2',
                      outfile='foo2_roi',
                      tmin=20,tsize=40,
                      xmin=3,xsize=30,
                      ymin=40,ysize=10,
                      zmin=5,zsize=20)
    yield assert_equal, roi2.cmdline, \
          'fslroi foo2 foo2_roi 3 30 40 10 5 20 20 40'

    roi3 = fsl.Fslroi()
    results=roi3.run(infile='foo3',
                     outfile='foo3_roi',
                     xmin=3,xsize=30,
                     ymin=40,ysize=10,
                     zmin=5,zsize=20)
    
    roi3_dim = [ roi3.inputs.xmin,roi3.inputs.xsize,roi3.inputs.ymin,roi3.inputs.ysize,
                 roi3.inputs.zmin,roi3.inputs.zsize,roi3.inputs.tmin,roi3.inputs.tsize]
    desired_dim = [ 3,30,40,10,5,20,None,None ]    
    yield assert_equal, roi3_dim, desired_dim
    
    yield assert_not_equal, results.runtime.returncode, 0
    yield assert_equal, results.interface.inputs.infile, 'foo3'
    yield assert_equal, results.interface.inputs.outfile, 'foo3_roi'
    yield assert_equal, results.runtime.cmdline, 'fslroi foo3 foo3_roi 3 30 40 10 5 20'

    # test arguments for opt_map
    # Fslroi class doesn't have a filled opt_map{}
    
    
# test fslmath 
def test_fslmaths():
    math = fsl.Fslmaths()

    # make sure command gets called
    yield assert_equal, math.cmd, 'fslmaths'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, math.run 

    # .inputs based parameters setting
    math.inputs.infile='foo.nii'
    math.inputs.optstring='-add 2.5 -mul input_volume2'
    math.inputs.outfile='foo_math.nii'
    
    yield assert_equal, math.cmdline, 'fslmaths foo.nii -add 2.5 -mul input_volume2 foo_math.nii'

    # .run based parameter setting
    math2 = fsl.Fslmaths(infile='foo2',optstring='-add 2.5',outfile='foo2_math')
    yield assert_equal, math2.cmdline, 'fslmaths foo2 -add 2.5 foo2_math'

    math3 = fsl.Fslmaths()
    results=math3.run(infile='foo',outfile='foo_math',optstring='-add input_volume2')
    yield assert_not_equal, results.runtime.returncode, 0
    yield assert_equal, results.interface.inputs.infile, 'foo'
    yield assert_equal, results.interface.inputs.outfile, 'foo_math'
    yield assert_equal, results.runtime.cmdline, 'fslmaths foo -add input_volume2 foo_math'

    # test arguments for opt_map
    # Fslmath class doesn't have opt_map{}
    

# test tbss_1_preproc    
def test_tbss_1_preproc():
    
    tbss1 = fsl.Tbss1preproc()

    # make sure command gets called
    yield assert_equal, tbss1.cmd, 'tbss_1_preproc'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, tbss1.run 
    
    # .inputs based parameters setting
    tbss1.inputs.infiles='foo.nii  f002.nii  f003.nii'
    yield assert_equal, tbss1.cmdline, 'tbss_1_preproc foo.nii  f002.nii  f003.nii'

    tbss = fsl.Tbss1preproc()
    results=tbss.run(infiles='*.nii.gz',noseTest=True)
    yield assert_equal, results.interface.inputs.infiles, '*.nii.gz'
    yield assert_equal, results.runtime.cmdline, 'tbss_1_preproc *.nii.gz'

    # test arguments for opt_map
    # Tbss_1_preproc class doesn't have opt_map{}
    
    

# test tbss_2_reg   
def test_tbss_2_reg():
    
    tbss2 = fsl.Tbss2reg()

    # make sure command gets called
    yield assert_equal, tbss2.cmd, 'tbss_2_reg'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, tbss2.run 

    # .inputs based parameters setting
    tbss2.inputs.FMRIB58_FA_1mm=True
    yield assert_equal, tbss2.cmdline, 'tbss_2_reg -T'

    # .run based parameter setting
    tbss22 = fsl.Tbss2reg(targetImage='targetImg')
    yield assert_equal, tbss22.cmdline,'tbss_2_reg -t targetImg'
    
    tbss222 = fsl.Tbss2reg(findTarget=True)
    yield assert_equal, tbss222.cmdline,'tbss_2_reg -n'

    tbss21 = fsl.Tbss2reg()
    results = tbss21.run(FMRIB58_FA_1mm=True,noseTest=True)
    yield assert_equal, results.runtime.cmdline, 'tbss_2_reg -T'
    
    # test arguments for opt_map
    opt_map ={ 'FMRIB58_FA_1mm':    ('-T', True),
               'targetImage':       ('-t allimgs', 'allimgs'),
               'findTarget':        ('-n', True)}

    for name, settings in opt_map.items():
        tbss = fsl.Tbss2reg(**{name: settings[1]})
        yield assert_equal, tbss.cmdline, tbss.cmd+' '+settings[0]

    
def test_tbss_3_postreg():    
    
    tbss = fsl.Tbss3postreg()

    # make sure command gets called
    yield assert_equal, tbss.cmd, 'tbss_3_postreg'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, tbss.run 

    # .inputs based parameters setting
    tbss.inputs.FMRIB58_FA=True
    yield assert_equal, tbss.cmdline, 'tbss_3_postreg -T'

    # .run based parameter setting
    tbss2 = fsl.Tbss3postreg(subject_means=True)
    yield assert_equal, tbss2.cmdline,'tbss_3_postreg -S'
    
    tbss3 = fsl.Tbss3postreg()
    results = tbss3.run(FMRIB58_FA=True,noseTest=True)
    yield assert_equal, results.runtime.cmdline, 'tbss_3_postreg -T'
    
    # test arguments for opt_map
    opt_map ={ 'subject_means':     ('-S',True),
               'FMRIB58_FA':        ('-T',True)}

    for name, settings in opt_map.items():
        tbss3 = fsl.Tbss3postreg(**{name: settings[1]})
        yield assert_equal, tbss3.cmdline, tbss3.cmd+' '+settings[0]

    
def test_tbss_4_prestats():
    tbss = fsl.Tbss4prestats()

    # make sure command gets called
    yield assert_equal, tbss.cmd, 'tbss_4_prestats'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, tbss.run

    # .inputs based parameters setting
    tbss.inputs.threshold=0.3
    yield assert_equal, tbss.cmdline,'tbss_4_prestats 0.3'
    
    tbss2 = fsl.Tbss4prestats(threshold=0.4)
    yield assert_equal, tbss2.cmdline,'tbss_4_prestats 0.4' 
    
    tbss3 = fsl.Tbss4prestats()
    results = tbss3.run(threshold=0.2,noseTest=True)
    yield assert_equal, results.runtime.cmdline, 'tbss_4_prestats 0.2'    

    # test arguments for opt_map
    # Tbss4prestats doesn't have an opt_map{}


    
def test_randomise():

    rand = fsl.Randomise()

    # make sure command gets called
    yield assert_equal, rand.cmd, 'randomise'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, rand.run 

    # .inputs based parameters setting
    rand.inputs.input_4D = 'infile.nii'
    rand.inputs.output_rootname = 'outfile'
    rand.inputs.design_matrix = 'design.mat'
    rand.inputs.t_contrast = 'infile.con'
    
    actualCmdline = sorted(rand.cmdline.split())
    cmd = 'randomise -i infile.nii -o outfile -d design.mat -t infile.con'
    desiredCmdline = sorted(cmd.split())    
    yield assert_equal, actualCmdline, desiredCmdline

    # .run based parameter setting
    rand2 = fsl.Randomise(input_4D='infile2',
                          output_rootname='outfile2',
                          f_contrast='infile.f',
                          one_sample_gmean=True,
                          int_seed=4)
              
    actualCmdline = sorted(rand2.cmdline.split())
    cmd = 'randomise -i infile2 -o outfile2 -1 -f infile.f --seed 4'
    desiredCmdline = sorted(cmd.split())    
    yield assert_equal, actualCmdline, desiredCmdline

    rand3=fsl.Randomise()
    results=rand3.run(input_4D='infile3',
                      output_rootname='outfile3')
    yield assert_equal, results.runtime.cmdline, \
          'randomise -i infile3 -o outfile3'    

    # test arguments for opt_map
    opt_map ={'demean_data':                        ('-D', True),
              'one_sample_gmean':                   ('-1', True),
              'mask_image':                         ('-m inp_mask', 'inp_mask'),
              'design_matrix':                      ('-d design.mat', 'design.mat'),
              't_contrast':                         ('-t input.con', 'input.con'),
              'f_contrast':                         ('-f input.fts', 'input.fts'),
              'xchange_block_labels':               ('-e design.grp', 'design.grp'),
              'print_unique_perm':                  ('-q', True),
              'print_info_parallelMode':            ('-Q', True),
              'num_permutations':                   ('-n 10', 10),
              'vox_pvalus':                         ('-x', True),
              'fstats_only':                        ('--fonly', True),
              'thresh_free_cluster':                ('-T', True),
              'thresh_free_cluster_2Dopt':          ('--T2', True),
              'cluster_thresholding':               ('-c 0.20', 0.20),
              'cluster_mass_thresholding':          ('-C 0.40', 0.40),
              'fcluster_thresholding':              ('-F 0.10', 0.10),
              'fcluster_mass_thresholding':         ('-S 0.30', 0.30),
              'variance_smoothing':                 ('-v 0.20', 0.20),
              'diagnostics_off':                    ('--quiet', True),
              'output_raw':                         ('-R', True),
              'output_perm_vect':                   ('-P', True),
              'int_seed':                           ('--seed 20', 20),
              'TFCE_height_param':                  ('--tfce_H 0.11', 0.11),
              'TFCE_extent_param':                  ('--tfce_E 0.50', 0.50),
              'TFCE_connectivity':                  ('--tfce_C 0.30', 0.30),
              'list_num_voxel_EVs_pos':             ('--vxl 1,2,3,4', '1,2,3,4'),
              'list_img_voxel_EVs':                 ('--vxf 6,7,8,9,3', '6,7,8,9,3')}

    for name, settings in opt_map.items():
        rand4 = fsl.Randomise(input_4D='infile',output_rootname='root',**{name: settings[1]})
        yield assert_equal, rand4.cmdline, rand4.cmd+' -i infile -o root '+settings[0]

    

def test_Randomise_parallel():
    rand = fsl.Randomise_parallel()

    # make sure command gets called
    yield assert_equal, rand.cmd, 'randomise_parallel'

    # test raising error with mandatory args absent
    yield assert_raises, AttributeError, rand.run 

    # .inputs based parameters setting
    rand.inputs.input_4D = 'infile.nii'
    rand.inputs.output_rootname = 'outfile'
    rand.inputs.design_matrix = 'design.mat'
    rand.inputs.t_contrast = 'infile.con'
    
    actualCmdline = sorted(rand.cmdline.split())
    cmd = 'randomise_parallel -i infile.nii -o outfile -d design.mat -t infile.con'
    desiredCmdline = sorted(cmd.split())    
    yield assert_equal, actualCmdline, desiredCmdline

    # .run based parameter setting
    rand2 = fsl.Randomise_parallel(input_4D='infile2',
                          output_rootname='outfile2',
                          f_contrast='infile.f',
                          one_sample_gmean=True,
                          int_seed=4)
              
    actualCmdline = sorted(rand2.cmdline.split())
    cmd = 'randomise_parallel -i infile2 -o outfile2 -1 -f infile.f --seed 4'
    desiredCmdline = sorted(cmd.split())    
    yield assert_equal, actualCmdline, desiredCmdline

    rand3=fsl.Randomise_parallel()
    results=rand3.run(input_4D='infile3',
                      output_rootname='outfile3')
    yield assert_equal, results.runtime.cmdline, \
          'randomise_parallel -i infile3 -o outfile3'    

    # test arguments for opt_map
    opt_map ={'demean_data':                        ('-D', True),
              'one_sample_gmean':                   ('-1', True),
              'mask_image':                         ('-m inp_mask', 'inp_mask'),
              'design_matrix':                      ('-d design.mat', 'design.mat'),
              't_contrast':                         ('-t input.con', 'input.con'),
              'f_contrast':                         ('-f input.fts', 'input.fts'),
              'xchange_block_labels':               ('-e design.grp', 'design.grp'),
              'print_unique_perm':                  ('-q', True),
              'print_info_parallelMode':            ('-Q', True),
              'num_permutations':                   ('-n 10', 10),
              'vox_pvalus':                         ('-x', True),
              'fstats_only':                        ('--fonly', True),
              'thresh_free_cluster':                ('-T', True),
              'thresh_free_cluster_2Dopt':          ('--T2', True),
              'cluster_thresholding':               ('-c 0.20', 0.20),
              'cluster_mass_thresholding':          ('-C 0.40', 0.40),
              'fcluster_thresholding':              ('-F 0.10', 0.10),
              'fcluster_mass_thresholding':         ('-S 0.30', 0.30),
              'variance_smoothing':                 ('-v 0.20', 0.20),
              'diagnostics_off':                    ('--quiet', True),
              'output_raw':                         ('-R', True),
              'output_perm_vect':                   ('-P', True),
              'int_seed':                           ('--seed 20', 20),
              'TFCE_height_param':                  ('--tfce_H 0.11', 0.11),
              'TFCE_extent_param':                  ('--tfce_E 0.50', 0.50),
              'TFCE_connectivity':                  ('--tfce_C 0.30', 0.30),
              'list_num_voxel_EVs_pos':             ('--vxl '+repr([1,2,3,4]), repr([1,2,3,4])),
              'list_img_voxel_EVs':                 ('--vxf '+repr([6,7,8,9,3]), repr([6,7,8,9,3]))}

    for name, settings in opt_map.items():
        rand4 = fsl.Randomise_parallel(input_4D='infile',output_rootname='root',**{name: settings[1]})
        yield assert_equal, rand4.cmdline, rand4.cmd+' -i infile -o root '+settings[0]



def test_fsl_sub():
    pass
    # make sure command gets called


    # test raising error with mandatory args absent


    # .inputs based parameters setting


    # .run based parameter setting


    # test generation of outfile


    # test arguments for opt_map
##     opt_map ={'EstimatedJobLength':            ('-T 0.22', 0.22),
##               'QueueType':                     ('-q long', 'long'),
##               'Architecture':                  ('-a amd64', 'amd64'),
##               'JobPriority':                   ('-p 0', 0),
##               'Email':                         ('-M %s',
##               'Hold':                          ('-j %d',
##               'CommandScript':                 ('-t %s',
##               'Jobname':                       ('-N %s',
##               'logFilePath':                   ('-l %s',
##               'SGEmailOpts':                   ('-m %s',
##               'ScriptFlags4SGEqueue':          ('-F',
##               'Verbose':                       ('-v'}
##     
##    for name, settings in opt_map.items():
##        fsub4 = fsl.Fsl_sub(input_4D='infile',output_rootname='root',**{name: settings[1]})
##        yield assert_equal, fsub4.cmdline, fsub4.cmd+' -i infile -o root '+settings[0]
##     


def test_Probtrackx():
    pass
    # make sure command gets called


    # test raising error with mandatory args absent


    # .inputs based parameters setting


    # .run based parameter setting


    # test generation of outfile


    # test arguments for opt_map


def test_Proj_thresh():
    pass
    # make sure command gets called


    # test raising error with mandatory args absent


    # .inputs based parameters setting


    # .run based parameter setting


    # test generation of outfile


    # test arguments for opt_map

    

def test_Find_the_biggest():
    pass
    # make sure command gets called


    # test raising error with mandatory args absent


    # .inputs based parameters setting


    # .run based parameter setting


    # test generation of outfile


    # test arguments for opt_map
    

    
#----------------------------------------------------------------------------------------------------------------


