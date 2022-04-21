import argparse
import yaml

class Config():
    def __init__(self, config):
        d = yaml.safe_load(config)
        print(d)

def main():
    parser = argparse.ArgumentParser(description="Download Jetbrain IDE plugins")
    parser.add_argument('-c', '--config-file', dest='config', type=argparse.FileType('r'), required=True)
    args = parser.parse_args()

    config = Config(args.config)

if __name__ == '__main__':
    main()
