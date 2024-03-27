from pycomm3 import LogixDriver

winder_plc_address = '192.168.140.13'

tags_to_read = ['X_Axis']
#     'X_Axis.ActualPosition', 'X_Axis.ActualVelocity', 'X_Axis.CommandAcceleration',
#     'X_Axis.CoordinatedMotionStatus', 'X_Axis.ModuleFault', 'Y_Axis.ActualPosition',
#     'Y_Axis.ActualVelocity', 'Y_Axis.CommandAcceleration', 'Y_Axis.CoordinatedMotionStatus',
#     'Y_Axis.ModuleFault', 'Z_Axis.ActualPosition', 'Z_Axis.ActualVelocity',
#     'Z_Axis.CommandAcceleration', 'Z_Axis.CoordinatedMotionStatus', 'Z_Axis.ModuleFault',
#     'STATE', 'ERROR_CODE', 'Cam_F:I.InspectionResults[0]', 'Cam_F:I.InspectionResults[1]',
#     'Cam_F:I.InspectionResults[2]', 'Cam_F:I.InspectionResults[3]', 'Machine_SW_Stat', 'MORE_STATS_S'
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

# Connect to the PLC
with LogixDriver(winder_plc_address) as plc:
    if plc:
    #     all_tags_data = read_all_tags(plc)
    #     for key in all_tags_data:
    #         print(key)
    # else:
    #     print("couldn't open connection")

        for tagname in tags_to_read:
            try:
                print(plc.read(tagname))
            except:
                print(f"error reading tag {tagname}")