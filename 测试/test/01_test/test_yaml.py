import yaml

if __name__ == '__main__':
    print(yaml.dump({'name': 'Silenthand Olleander', 'race': 'Human','traits': ['ONE_HAND', 'ONE_EYE']}))
    data = {'name': 'Silenthand Olleander', 'race': 'Human','traits': ['ONE_HAND', 'ONE_EYE']}
    stream = open('test.yaml', 'w')
    yaml.dump(data, stream)