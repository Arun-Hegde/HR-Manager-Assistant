from mcp.server.fastmcp import FastMCP
from HRMS import *
from utils import seed_services
from typing import List,Dict,Optional
from emails import EmailSender
import os
from dotenv import load_dotenv

_ = load_dotenv()

emailer = EmailSender(
        smtp_server="smtp.gmail.com",
        port=587,
        username=os.getenv("EMAIL_ID"),
        password=os.getenv("EMAIL_PWD"),
        use_tls=True)

mcp = FastMCP("HR-Assistant")

employee_manager = EmployeeManager()
leave_manager = LeaveManager()
ticket_manager = TicketManager()
meeting_manager = MeetingManager()

seed_services(employee_manager,leave_manager,meeting_manager,ticket_manager)
#tools
#resources (knowledge)
#prompts

@mcp.tool()
def add_employee(emp_name:str,manager_id:str,email:str)-> str:
    """
    Add a new employee to the HRMS system.
    :param emp_name: Employee Name
    :param manager_id: Manager ID (optional)
    :param email: email
    :return: Configuration Message
    """
    emp = EmployeeCreate(
    emp_id=employee_manager.get_next_emp_id(),
    name = emp_name,
    email=email,
    manager_id=manager_id
    )
    employee_manager.add_employee(emp)
    return f"Employee {emp_name} added successfully"

@mcp.tool()
def get_employee_details(name: str)-> Dict[str,str]:
    """
    Get employee details by name
    :param name: name of the employee
    :return: Employee ID and Manager ID
    """
    matches = employee_manager.search_employee_by_name(name)
    if len(matches) == 0:
        raise ValueError(f"NO Employees found matching '{name}'")
    emp_id = matches[0]
    return employee_manager.get_employee_details(emp_id)

@mcp.tool()
def send_email(to_emails: List[str], subject: str, body: str, html: bool = False) -> None:
    emailer.send_email(subject, body, to_emails, from_email=emailer.username, html=html)
    return "Email sent successfully."

@mcp.tool()
def create_ticket(emp_id:str,item:str,reason:str) -> str:
    """
       Create a ticket for buying required items for an employee.
       :param emp_id: Employee ID
       :param item: Item requested (Laptop, ID Card, etc.)
       :param reason: Reason for the request
       :return: Confirmation message
       """
    ticket_req = TicketCreate(
        emp_id=emp_id,
        item=item,
        reason=reason
    )
    return ticket_manager.create_ticket(ticket_req)

@mcp.tool()
def update_ticket_status(ticket_id:str,status:str) -> str:
    """
    update the status of the ticket
    :param ticket_id: Ticket ID
    :param status: New Status of the Ticket
    :return: Confirmation message
    """
    ticket_status_update = TicketStatusUpdate(status=status)
    return ticket_manager.update_ticket_status(ticket_status_update,ticket_id)

@mcp.tool()
def list_tickets(employee_id:str,status:str) -> List[Dict[str,str]]:
    """
    List tickets for an employee with optional status filter.
    :param employee_id: Employee ID
    :param status: Ticket Status (Optional)
    :return: List Of Tickets
    """
    return ticket_manager.list_tickets(employee_id=employee_id,status=status)

@mcp.tool()
def schedule_meeting(emp_id:str,meeting_dt:datetime,topic:str)->str:
    """
    Schedule Meeting For the Employee
    :param emp_id: Employee ID
    :param meeting_dt : Date and time of the Scheduled meeting in python datetime format
    :param topic: Topic of the meeting
    :return: Confirmation message
    """
    meeting_req = MeetingCreate(emp_id=emp_id, meeting_dt=meeting_dt, topic=topic)
    return meeting_manager.schedule_meeting(meeting_req)

@mcp.tool()
def get_meetings(employee_id:str)-> List:
    """
    Get the list of meetings scheduled for an employee.
    :param employee_id: Employee ID
    :return: List Of meetings
    """
    return meeting_manager.get_meetings(employee_id=employee_id)

@mcp.tool()
def cancel_meeting(employee_id:str,meeting_dt:datetime,topic:str)-> str:
    """
    Cancel The scheduled Meeting For an Employee.
    :param employee_id: Employee ID
    :param meeting_dt: Date and Time of Meeting in python datetime format
    :param topic: Topic of the meeting (Optional)
    :return: Confirmation message
    """
    meeting_cancel_req = MeetingCancelRequest(emp_id=employee_id,meeting_dt=meeting_dt, topic=topic)
    return meeting_manager.cancel_meeting(meeting_cancel_req)

@mcp.tool()
def get_leave_balance(employee_id:str)-> str:
    """
    Get leave balance of the Employee
    :param employee_id: Employee ID
    :return: Employee ID with Remaining Leaves
    """
    return leave_manager.get_leave_balance(employee_id=employee_id)

@mcp.tool()
def apply_leave(employee_id:str,leave_dates:List)-> str:
    """
    Apply a leave for the Employee for the given Dates
    :param employee_id: Employee ID
    :param leave_dates: List of Leave Dates
    :return: Leave Application status message
    """
    leave_req = LeaveApplyRequest(emp_id=employee_id,leave_dates=leave_dates)
    return leave_manager.apply_leave(leave_req)

@mcp.tool()
def get_leave_history(employee_id:str)-> str:
    """
    Get the leave history for the Employee.
    :param employee_id: Employee ID
    :return: Employee ID with leave Date History
    """
    return leave_manager.get_leave_history(employee_id=employee_id)

@mcp.prompt("onboard_new_employee")
def onboard_new_employee(employee_name: str,manager_name:str):
    return f"""
    Onboard a new employee with the following details:
    - Name: {employee_name}
    - Manager Name: {manager_name}
    Steps to follow:
    - Add the employee to HRMS system.
    - Send a welcome email to the employee with their login credentials. ( Format: employee_name@atliq.com)  
    - Notify the manager about the new  employee's onboarding.
    - Raise tickets for new laptop , id card , and other necessary equipment. 
    - Schedule an Introduction meeting with the onboarded Employee and Manager.
    """

if __name__ == "__main__":
    mcp.run(transport='stdio')