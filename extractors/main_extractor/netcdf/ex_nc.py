from netCDF4 import Dataset
import json, os
import numpy as np
import sys

'''
    This is the code for the NetCDF extractor.  This takes a file deemed a NetCDF file and extracts all metadata from it
    as a JSON.

    @Inputs: file_handle -- opened NetCDF file.
    @Outputs: metadata -- metadata JSON

    @Author: Tyler J. Skluzacek, derived from code by Paul Beckman.
    @LastEdited: 07/27/2017
'''

class ExtractionFailed(Exception):
    """Basic error to throw when an extractor fails"""


class ExtractionPassed(Exception):
    """Indicator to throw when extractor passes for fast file classification"""

class NumpyDecoder(json.JSONEncoder):
    """Serializer used to convert numpy types to normal json serializable types.
    Since netCDF4 produces numpy types, this is necessary for compatibility with
    other metadata scrapers like the csv, which returns a python dict"""

    def default(self, obj):
        if isinstance(obj, np.generic):
            return np.asscalar(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.dtype):
            return str(obj)
        else:
            return super(NumpyDecoder, self).default(obj)



def extract_netcdf_metadata(file_handle, pass_fail=False):
    """Create netcdf metadata JSON from file.
        :param file_handle: (str) file
        :param pass_fail: (bool) whether to exit after ascertaining file class
        :returns: (dict) metadata dictionary"""

    try:
        dataset = Dataset(os.path.realpath(file_handle.name))
    except IOError:
        raise ExtractionFailed

    if pass_fail:
        raise ExtractionPassed

    metadata = {
        "file_format": dataset.file_format,
    }
    if len(dataset.ncattrs()) > 0:
        metadata["global_attributes"] = {}
    for attr in dataset.ncattrs():
        metadata["global_attributes"][attr] = dataset.getncattr(attr)

    dims = dataset.dimensions
    if len(dims) > 0:
        metadata["dimensions"] = {}
    for dim in dims:
        metadata["dimensions"][dim] = {
            "size": len(dataset.dimensions[dim])
        }
        add_ncattr_metadata(dataset, dim, "dimensions", metadata)

    vars = dataset.variables
    if len(vars) > 0:
        metadata["variables"] = {}
    for var in vars:
        if var not in dims:
            metadata["variables"][var] = {
                "dimensions": dataset.variables[var].dimensions,
                "size": dataset.variables[var].size
            }
        add_ncattr_metadata(dataset, var, "variables", metadata)

    # cast all numpy types to native python types via dumps, then back to dict via loads
    return json.loads(json.dumps(metadata, cls=NumpyDecoder))

def add_ncattr_metadata(dataset, name, dim_or_var, metadata):
    """Get attributes from a netCDF variable or dimension.
        :param dataset: (netCDF4.Dataset) dataset from which to extract metadata
        :param name: (str) name of attribute
        :param dim_or_var: ("dimensions" | "variables") metadata key for attribute info
        :param metadata: (dict) dictionary to add this attribute info to"""

    try:
        metadata[dim_or_var][name]["type"] = dataset.variables[name].dtype
        for attr in dataset.variables[name].ncattrs():
            metadata[dim_or_var][name][attr] = dataset.variables[name].getncattr(attr)
    # some variables have no attributes
    except KeyError:
        pass

import time

# TODO: Tyler, what the hell?

t0 = time.time()
with open('/home/skluzacek/Downloads/pub8/oceans/CLIVAR/ARC01_33HQ20150809/33HQ20150809_00063_00001_ctd.nc', 'rb') as f:
    extract_netcdf_metadata(f)
t1 = time.time()

print(t1-t0)

