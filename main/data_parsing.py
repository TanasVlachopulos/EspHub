import json

from DataAccess import DBA, DAO
from DeviceCom import DataSender
from Config import Config

conf = Config.Config().get_config()


def get_actual_device_values(device_id, io_type='all'):
    db = DBA.Dba(conf.get('db', 'path'))
    device = db.get_device(device_id)

    device_values = []
    if device:
        try:
            abilities = json.loads(device.provided_func)
        except json.JSONDecodeError as e:
            print(conf.get('msg', 'decode_error'))
            abilities = []

        for ability in abilities:
            # get newest record from db
            records = db.get_record_from_device(device_id, value_type=ability['name'], limit=1)

            # select type of ability
            if ability['io'] == io_type or io_type == 'all':
                # select first item from record list or create empty dictionary if record list is empty
                if len(records) > 0:
                    record_dict = records[0].__dict__
                    record_dict['time'] = records[0].time
                else:
                    record_dict = {}

                record_dict['value_type'] = ability['user_name']
                record_dict['unit'] = ability['unit']
                record_dict['category'] = ability['category']
                record_dict['io'] = ability['io']
                record_dict['desc'] = ability['desc']
                record_dict['user_name'] = ability['user_name']
                record_dict['name'] = ability['name']
                device_values.append(record_dict)

    return device_values


def get_records_for_charts(device_id, value_type, from_date, to_date):
    db = DBA.Dba(conf.get('db', 'path'))
    records = db.get_record_from_device(device_id, value_type, limit=300)

    values = [float(record.value) for record in records]
    values.reverse()

    response = {
        # convert datetime objects to isoformat strings in reverse order
        'labels': list(reversed([record.time.isoformat() for record in records])),
        'values': values,
    }

    return response


def get_all_input_abilities():
    db = DBA.Dba(conf.get('db', 'path'))
    records = db.get_devices()
    output = []
    for record in records:
        abilities = json.loads(record.provided_func)
        output_record = {'name': record.name}
        abilities_list = []
        for ability in abilities:
            if ability['io'] == 'in':
                abilities_list.append(ability)

        if len(abilities_list) != 0:
            output_record['abilities'] = abilities_list
            output.append(output_record)

    return output