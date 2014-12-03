import os
import netCDF4 as nc
import numpy
import pyresample

from satistjenesten import data
from satistjenesten import retrievals

@given(u'we process file {netcdf_filepath}')
def step_impl(context, netcdf_filepath):
	context.netcdf_filepath = netcdf_filepath

@then(u'load the file using yaml config {avhrr_l1b_yaml_config}')
def step_impl(context, avhrr_l1b_yaml_config):
	context.config_filepath = avhrr_l1b_yaml_config
	scene = data.SatScene()
	scene.config_filepath = context.config_filepath
	scene.input_filename = context.netcdf_filepath
	scene.load_scene_from_disk()
	expected_variable = nc.Dataset(context.netcdf_filepath).variables['reflec_1'][:]
	numpy.testing.assert_array_almost_equal(scene.bands['reflec_1'].data,expected_variable)
	context.scene = scene

@then(u'resample it to the istjenesten generic area {area_name}')
def step_impl(context, area_name):
        context.area_name = area_name
	context.scene.area_name = context.area_name
 	context.gridded_scene = context.scene.resample_to_area()
        area_def = pyresample.utils.load_area('areas.cfg', context.area_name)
        expected_dimensions = area_def.shape
        tested_dimensions = context.gridded_scene.bands.items()[0][1].data.shape
        assert expected_dimensions == tested_dimensions

@then(u'export it as a netcdf file {output_file}')
def step_impl(context, output_file):
	context.output_file = output_file
        context.scene.output_filepath = context.output_file
	context.scene.write_as_netcdf()
        # compare the exported results with the area definition
        os.path.exists(context.output_file)
        os.remove(context.output_file)

@then(u'resample it to the GAC format')
def step_impl(context):
        scene = context.scene
        scene.resample_to_gac()
        gac_data = scene.bands.values()[0].data
        assert isinstance(gac_data, numpy.ndarray)
        gac_data_scan_width = 400 # pixels
        assert gac_data.shape[1] == gac_data_scan_width

@given(u'using AVHRR L1B Beam config')
def step_impl(context):
    context.config_filepath = 'files/avhrr_beam.yml'
    assert os.path.exists(context.config_filepath)

@when(u'processing {input_file} file')
def step_impl(context, input_file):
    context.input_file = input_file
    assert os.path.exists(context.input_file)
    # load file contents
    swath_scene = data.SatScene()
    swath_scene.config_filepath = context.config_filepath
    swath_scene.input_filename = context.input_file
    swath_scene.load_scene_from_disk()
    assert swath_scene.bands is not None
    context.swath_scene = swath_scene


@when(u'computing sic using {sic_algorithm} algorithm')
def step_impl(context, sic_algorithm):
    scene = context.swath_scene
    retrievals.compute_parameter(scene, alg=sic_algorithm)
    assert numpy.mean(scene.bands['sic'].data) == 1

@then(u'get file with sic data')
def step_impl(context):
    assert False

@then(u'with mean sic value 1')
def step_impl(context):
    assert False
