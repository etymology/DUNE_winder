from pycomm3 import LogixDriver

winder_plc_address = '192.168.140.13'

tags_to_read = ['X_axis']
#     'X_axis.ActualPosition', 'X_axis.ActualVelocity', 'X_axis.CommandAcceleration',
#     'X_axis.CoordinatedMotionStatus', 'X_axis.ModuleFault', 'Y_axis.ActualPosition',
#     'Y_axis.ActualVelocity', 'Y_axis.CommandAcceleration', 'Y_axis.CoordinatedMotionStatus',
#     'Y_axis.ModuleFault', 'Z_axis.ActualPosition', 'Z_axis.ActualVelocity',
#     'Z_axis.CommandAcceleration', 'Z_axis.CoordinatedMotionStatus', 'Z_axis.ModuleFault',
#     'STATE', 'ERROR_CODE', 'Cam_F:I.InspectionResults[0]', 'Cam_F:I.InspectionResults[1]',
#     'Cam_F:I.InspectionResults[2]', 'Cam_F:I.InspectionResults[3]', 'MACHINE_SW_STAT', 'MORE_STATS_S'
# ]

def read_all_tags(plc):
    all_tags_data = {}
    for tag_name, tag_obj in plc.tags.items():
        try:
            tag_value = plc.read(tag_name)
            all_tags_data[tag_name] = tag_value
        except Exception as e:
            print(f"Error reading tag {tag_name}: {e}")
            all_tags_data[tag_name] = None
    return all_tags_data


if __name__ == "__main__":
    # # Connect to the PLC
    with LogixDriver(winder_plc_address) as plc:
        all_tags_data = read_all_tags(plc)
        for key in all_tags_data:
            print(key)
        print(plc.read('X_axis.ModuleFault'))
