from .get_calendar_schedule import (
    get_calendar_schedule_tool,
    start_get_calendar_schedule,
    get_calendar_schedule,
)
from .schedule_appointment import (
    schedule_appointment_tool,
    start_schedule_appointment,
    schedule_appointment,
)
from .search_insurance_policies import (
    search_insurance_policies_tool,
    start_search_insurance_policies,
    search_insurance_policies,
)

tools = [
    get_calendar_schedule_tool,
    schedule_appointment_tool,
    search_insurance_policies_tool,
]

functions = {
    "get_calendar_schedule": {
        "start_callback": start_get_calendar_schedule,
        "callback": get_calendar_schedule,
    },
    "schedule_appointment": {
        "start_callback": start_schedule_appointment,
        "callback": schedule_appointment,
    },
    "search_insurance_policies": {
        "start_callback": start_search_insurance_policies,
        "callback": search_insurance_policies,
    },
}
