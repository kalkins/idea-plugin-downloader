import argparse
import logging
import yaml
import re
from xml.etree import ElementTree as ET
from urllib import request
from urllib.parse import urlencode
from pathlib import Path

class Config():
    def __init__(self, args):
        d = yaml.safe_load(args.config)
        logger.debug(f'Loading config: {d}')

        self.versions = d['versions']
        self.plugins = d['plugins']

        self.mirror = d.get('mirror_url', 'https://plugins.jetbrains.com')

        self.output_path = args.output_path

def fetch_available_plugins(version, config):
    url = f'{config.mirror}/plugins/list/?build={version}'
    logger.debug(f'Fetching plugin list for version {version} from {url}')
    xml = ET.parse(request.urlopen(url))

    return [
        {
            'id': plugin.find('id').text,
            'version': plugin.find('version').text,
            'idea_version': plugin.find('idea-version').attrib,
            'name': plugin.find('name').text,
            'description': plugin.find('description').text,
            'change_notes': plugin.find('change-notes').text,
            'dependencies': [dep.text for dep in plugin.findall('depends') if '(optional)' not in dep.text],
            'optional_dependencies': [dep.text.replace('(optional) ', '') for dep in plugin.findall('depends') if '(optional)' in dep.text],
        }
        for plugin in xml.getroot().iter('idea-plugin')
    ]

def compile_plugin_list(config):
    plugin_list = {}

    for version in config.versions:
        available_plugins = fetch_available_plugins(version, config)

        def add_plugins(plugins):
            for plugin in plugins:
                if 'com.intellij.modules' in plugin:
                    continue

                for p in available_plugins:
                    if p['id'] == plugin or p['name'] == plugin:
                        metadata = p
                        plugin_id = metadata['id']
                        plugin_version = metadata['version']
                        break
                else:
                    logger.warning(f'Plugin {plugin} not available for version {version}')
                    continue

                if plugin_id in plugin_list:
                    if plugin_version in plugin_list[plugin_id]:
                        logger.debug(f'Plugin {plugin} is already added to download queue. Skipping.')
                        continue
                    else:
                        plugin_list[plugin_id][plugin_version] = metadata
                else:
                    plugin_list[metadata['id']] = {plugin_version: metadata}

                add_plugins(metadata['dependencies'])
                add_plugins(metadata['optional_dependencies'])

        add_plugins(config.plugins)

    return plugin_list

def download_plugins(config):
    xml_root = ET.Element('plugins')

    for plugin_id, version_dict in compile_plugin_list(config).items():
        for plugin_version, metadata in version_dict.items():
            url = f'{config.mirror}/plugin/download?{urlencode({"pluginId": plugin_id, "version": plugin_version})}'
            logger.debug(f'Downloading plugin {plugin_id} version {plugin_version} from {url}')

            path = config.output_path / f'{plugin_id}-{plugin_version}.zip'
            if path.is_file():
                logger.info(f'Plugin {plugin_id} version {plugin_version} already downloaded.')
            else:
                response = request.urlopen(url)

                if response.status != 200:
                    logger.warning(f'Could not download plugin {plugin_id} version {plugin_version}. HTTP status {response.status}')
                    continue

                with open(path, 'wb') as f:
                    f.write(response.read())

            xml_plugin = ET.SubElement(xml_root, 'plugin', attrib={'id': metadata['id'], 'version': metadata['version'], 'url': path.name})
            ET.SubElement(xml_plugin, 'idea-version', attrib=metadata['idea_version'])
            ET.SubElement(xml_plugin, 'name').text = metadata['name']
            ET.SubElement(xml_plugin, 'description').text = metadata['description']
            ET.SubElement(xml_plugin, 'change-notes').text = metadata['change_notes']
            logger.info(f'Downloaded plugin {plugin_id} version {plugin_version}.')

    tree = ET.ElementTree(xml_root)
    ET.indent(tree)
    tree.write(config.output_path / 'updatePlugins.xml')
    #with open(config.output_path / 'updatePlugins.xml', 'wb') as f:
    #    f.write(ET.tostring())

    logger.info('Updated updatePlugins.xml')

def main(args):
    config = Config(args)
    download_plugins(config)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download Jetbrain IDE plugins")
    parser.add_argument('-c', '--config-file', dest='config', type=argparse.FileType('r'), required=True)
    parser.add_argument('-o', '--output-dir', dest='output_path', type=Path, default='.')
    parser.add_argument('-v', '--verbose', dest='verbosity', action='count', default=0)
    args = parser.parse_args()

    if args.verbosity == 0:
        log_level = 'WARNING'
    elif args.verbosity == 1:
        log_level = 'INFO'
    else:
        log_level = 'DEBUG'

    logging.basicConfig(level=log_level)

    main(args)
