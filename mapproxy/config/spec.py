# This file is part of the MapProxy project.
# Copyright (C) 2011 Omniscale <http://omniscale.de>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mapproxy.util.ext.dictspec.validator import validate, ValidationError
from mapproxy.util.ext.dictspec.spec import one_off, anything, number
from mapproxy.util.ext.dictspec.spec import recursive, required, type_spec, combined


def validate_mapproxy_conf(conf_dict):
    """
    Validate `conf_dict` agains mapproxy.yaml spec.
    Returns lists with errors. List is empty when no errors where found.
    """
    try:
        validate(mapproxy_yaml_spec, conf_dict)
    except ValidationError, ex:
        return ex.errors, ex.informal_only
    else:
        return [], True

coverage = {
    'polygons': str(),
    'polygons_srs': str(),
    'bbox': one_off(str(), [number()]),
    'bbox_srs': str(),
    'ogr_datasource': str(),
    'ogr_where': str(),
    'ogr_srs': str(),
}
image_opts = {
    'mode': str(),
    'colors': number(),
    'transparent': bool(),
    'resampling_method': str(),
    'format': str(),
    'encoding_options': {
        anything(): anything()
    }
}

http_opts = {
    'method': str(),
    'timeout': number(),
    'ssl_no_cert_checks': bool(),
}
mapserver_opts = {
    'binary': str(),
    'working_dir': str(),
}

scale_hints = {
    'max_scale': number(),
    'min_scale': number(),
    'max_res': number(),
    'min_res': number(),
}

source_commons = combined(
    scale_hints,
    {
        'concurrent_requests': int(),
        'coverage': coverage,
        'seed_only': bool(),
    }
)

mapproxy_yaml_spec = {
    'globals': {
        'image': {
            'resampling_method': 'method',
            'paletted': bool(),
            'stretch_factor': number(),
            'max_shrink_factor': number(),
            'jpeg_quality': number(),
            'formats': {
                anything(): image_opts,
            }
        },
        'http': {
            'timeout': number(),
        },
        'cache': {
            'base_dir': str(),
            'lock_dir': str(),
            'meta_size': [number()],
            'meta_buffer': number(),
            'minimize_meta_requests': bool(),
            'concurrent_tile_creators': int(),
        },
        'grid': {
            'tile_size': [int()],
        },
        'srs': {
          'axis_order_ne': [str()],
          'axis_order_en': [str()],
          'proj_data_dir': str(),
        },
        'mapserver': mapserver_opts,
    },
    'grids': {
        anything(): {
            'base': str(),
            'name': str(),
            'srs': str(),
            'bbox': one_off(str(), [number()]),
            'bbox_srs': str(),
            'num_levels': str(),
            'res': [number()],
            'res_factor': one_off(number(), str()),
            'max_res': number(),
            'min_res': number(),
            'stretch_factor': number(),
            'max_shrink_factor': number(),
            'align_resolutions_with': str(),
            'origin': str(),
            'tile_size': [int()],
            'threshold_res': [number()],
        }
    },
    'caches': {
        anything(): {
            required('sources'): [str()],
            'name': str(),
            'grids': [str()],
            'cache_dir': str(),
            'meta_size': [number()],
            'meta_buffer': number(),
            'minimize_meta_requests': bool(),
            'concurrent_tile_creators': int(),
            'disable_storage': bool(),
            'format': str(),
            'image': image_opts,
            'request_format': str(),
            'use_direct_from_level': number(),
            'use_direct_from_res': number(),
            'link_single_color_images': bool(),
            'watermark': {
                'text': basestring,
                'font_size': number(),
                'opacity': number(),
                'spacing': str(),
            }
        }
    },
    'services': {
        'demo': {},
        'kml': {},
        'tms': {},
        'wmts': {},
        'wms': {
            'srs': [str()],
            'image_formats': [str()],
            'attribution': {
                'text': basestring,
            },
            'featureinfo_types': [str()],
            'featureinfo_xslt': {
                anything(): str()
            },
            'source_errors': str(),
            'md': {
                'title': basestring,
                'abstract': basestring,
                'online_resource': basestring,
                'contact': anything(),
                'fees': basestring,
                'access_constraints': basestring,
            },
        },
    },
    
    'sources': {
        anything(): type_spec('type', {
            'wms': combined(source_commons, {
                'wms_opts': {
                    'version': str(),
                    'map': bool(),
                    'featureinfo': bool(),
                    'legendgraphic': bool(),
                    'legendurl': str(),
                    'featureinfo_format': str(),
                    'featureinfo_xslt': str(),
                },
                'image': combined(image_opts, {
                    'opacity':number(),
                    'transparent_color': one_off(str(), [number()]),
                    'transparent_color_tolerance': number(),
                }),
                'supported_formats': [str()],
                'supported_srs': [str()],
                'http': http_opts,
                required('req'): {
                    required('url'): str(),
                    anything(): anything()
                }
            }),
            'mapserver': combined(source_commons, {
                    'wms_opts': {
                        'version': str(),
                        'map': bool(),
                        'featureinfo': bool(),
                        'legendgraphic': bool(),
                        'legendurl': str(),
                    },
                    'image': combined(image_opts, {
                        'opacity':number(),
                        'transparent_color': one_off(str(), [number()]),
                        'transparent_color_tolerance': number(),
                    }),
                    'req': {
                        anything(): anything()
                    },
                    'mapserver': mapserver_opts,
            }),
            'tile': combined(source_commons, {
                required('url'): str(),
                'transparent': bool(),
                'grid': str(),
                'request_format': str(),
                'origin': str(),
                'http': http_opts,
            }),
            'mapnik': combined(source_commons, {
                required('mapfile'): str(),
                'transparent': bool(),
            }),
            'debug': {
            },
        })
    },
    
    'layers': one_off(
        {
            anything(): combined(scale_hints, {
                'sources': [str()],
                required('title'): str(),
                'legendurl': str(),
            })
        },
        recursive([combined(scale_hints, {
            'sources': [str()],
            'name': str(),
            required('title'): basestring,
            'legendurl': str(),
            'layers': [recursive()],
            
        })])
    ),
}

if __name__ == '__main__':
    import sys
    import yaml
    for f in sys.argv[1:]:
        data = yaml.load(open(f))
        try:
            validate(mapproxy_yaml_spec, data)
        except ValidationError, ex:
            for err in ex.errors:
                print '%s: %s' % (f, err)