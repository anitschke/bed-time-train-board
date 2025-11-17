# Leaving the Direction defined here since that is where it is defined in the
# upstream anitschke/childrens-museum-franklin-train-board repo.

# Direction Enum
# 
# WARNING: this enum is specific to the Franklin MBTA station. From
# https://api-v3.mbta.com/docs/swagger/index.html
# 
#   direction_id    integer Direction in which trip is traveling: 0 or 1.
#   
#   The meaning of direction_id varies based on the route. You can
#   programmatically get the direction names from /routes
#   /data/{index}/attributes/direction_names or /routes/{id}
#   /data/attributes/direction_names.
#
# Since we are setting this up for the Franklin line we will just hard code this
# for now. Looking at https://api-v3.mbta.com/routes/CR-Franklin we can see:
# 
#  "direction_names": [ "Outbound", "Inbound" ],
class Direction:
    OUT_BOUND = 0
    IN_BOUND = 1

def direction_str(direction):
    if direction == Direction.OUT_BOUND:
        return "OUT"
    if direction == Direction.IN_BOUND:
        return "IN"
    return "UNKNOWN"
