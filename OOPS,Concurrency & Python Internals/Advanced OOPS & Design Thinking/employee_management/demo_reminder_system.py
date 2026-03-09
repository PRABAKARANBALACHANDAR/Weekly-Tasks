import sys 
import os 

sys .path .append (os .path .dirname (os .path .abspath (__file__ )))

from utils .reminder_notification_manager import ReminderNotificationManager 
from utils .json_handler import JSONHandler 

def demonstrate_reminder_system ():

    print ("="*80 )
    print ("TASK REMINDER NOTIFICATION SYSTEM DEMONSTRATION")
    print ("="*80 )

    print ("\n[Step 1] Initializing Reminder Notification Manager...")
    reminder_manager =ReminderNotificationManager ()
    print ("[OK] Manager initialized")
    print (f"  - Notification file: data/reminder_notifications.json")
    print (f"  - Log file: data/reminder_logs.log")

    print ("\n[Step 2] Checking for upcoming project deadlines...")
    upcoming =reminder_manager .check_upcoming_deadlines (hours_threshold =48 )

    if not upcoming :
        print ("[OK] No upcoming deadlines within 48 hours")
    else :
        print (f"[OK] Found {len (upcoming )} project(s) with approaching deadlines:")
        for proj in upcoming :
            print (f"  - {proj ['project_id']}: '{proj ['title']}'")
            print (f"    Deadline: {proj ['deadline']} ({proj ['timezone']})")
            print (f"    Time Remaining: {proj ['time_remaining_str']}")
            print (f"    Assigned to Team: {proj ['team_id']}")

    print ("\n[Step 3] Creating reminder notifications...")
    created_reminders =[]

    for proj in upcoming :

        existing =reminder_manager .get_pending_notifications ()
        already_exists =any (n ['project_id']==proj ['project_id']for n in existing )

        if not already_exists :
            reminder_id =reminder_manager .create_reminder_notification (
            proj ['project_id'],
            proj ['team_id'],
            proj ['hours_remaining'],
            proj ['time_remaining_str']
            )
            created_reminders .append (reminder_id )
            print (f"[OK] Created reminder: {reminder_id }")
        else :
            print (f"  Reminder already exists for project: {proj ['project_id']}")

    print ("\n[Step 4] Viewing all pending reminders...")
    all_pending =reminder_manager .get_pending_notifications ()

    if not all_pending :
        print ("  No pending reminders")
    else :
        print (f"  Total pending reminders: {len (all_pending )}")
        for notif in all_pending :
            print (f"\n  Notification ID: {notif ['notification_id']}")
            print (f"    Project: {notif ['project_id']}")
            print (f"    Team: {notif ['team_id']}")
            print (f"    Time Remaining: {notif ['time_remaining_str']}")
            print (f"    Times Notified: {notif ['notification_count']}")
            print (f"    Acknowledged: {notif ['acknowledged']}")

    print ("\n[Step 5] Simulating reminder display to Team Lead...")

    teams =JSONHandler .load ('teams.json')
    if teams :

        first_team_id =list (teams .keys ())[0 ]
        team_data =teams [first_team_id ]
        leader_id =team_data .get ('team_leader_id')

        print (f"  Team: {first_team_id }")
        print (f"  Team Leader: {leader_id }")

        displayed =reminder_manager .display_pending_reminders (leader_id )

        if displayed :
            print (f"\n  Displayed {len (displayed )} reminder(s) to employee {leader_id }")
            print ("  Note: Notification counts incremented and logged")
        else :
            print ("  No pending reminders for this employee")
    else :
        print ("  No teams found in system")

    print ("\n[Step 6] Demonstrating reminder acknowledgment...")

    if all_pending :

        first_notif =all_pending [0 ]
        notif_id =first_notif ['notification_id']

        team_id =first_notif ['team_id']
        teams =JSONHandler .load ('teams.json')
        team_data =teams .get (team_id ,{})
        leader_id =team_data .get ('team_leader_id','UNKNOWN')

        print (f"  Team Lead {leader_id } acknowledging notification {notif_id }...")

        success =reminder_manager .acknowledge_notification (notif_id ,leader_id )

        if success :
            print ("  [OK] Notification acknowledged successfully")
            print ("  [OK] Acknowledgment logged")
            print ("  [OK] This reminder will no longer appear")
        else :
            print ("  [FAILED] Failed to acknowledge notification")
    else :
        print ("  No notifications to acknowledge")

    print ("\n[Step 7] Notification Summary...")
    if teams :
        first_team =list (teams .values ())[0 ]
        leader_id =first_team .get ('team_leader_id')

        summary =reminder_manager .get_notification_summary (leader_id )
        print (f"  Employee {leader_id }:")
        print (f"    Pending Reminders: {summary ['count']}")

    print ("\n[Step 8] Logging Information...")
    print ("  All notification events are logged to: data/reminder_logs.log")
    print ("  Log entries include:")
    print ("    - NOTIFICATION_CREATED: When a new reminder is created")
    print ("    - NOTIFICATION_SHOWN: Each time a reminder is displayed")
    print ("    - ACKNOWLEDGMENT_RECEIVED: When an employee acknowledges")
    print ("\n  Check the log file to see the complete audit trail!")

    print ("\n"+"="*80 )
    print ("DEMONSTRATION COMPLETE")
    print ("="*80 )
    print ("\nKey Features Demonstrated:")
    print ("  [OK] Automatic deadline monitoring")
    print ("  [OK] Persistent notification tracking")
    print ("  [OK] Repeated reminders until acknowledged")
    print ("  [OK] Comprehensive event logging")
    print ("  [OK] Employee-specific notification filtering")
    print ("  [OK] Acknowledgment system")

    print ("\nIntegration with Employee Management System:")
    print ("  1. Call check_upcoming_deadlines() periodically (e.g., on login)")
    print ("  2. Call display_pending_reminders(employee_id) when employee logs in")
    print ("  3. Provide option to acknowledge reminders in employee menu")
    print ("  4. Review logs in data/reminder_logs.log for audit trail")

def check_and_create_reminders ():

    print ("\nChecking for new deadlines to remind about...")

    reminder_manager =ReminderNotificationManager ()
    upcoming =reminder_manager .check_upcoming_deadlines (hours_threshold =24 )

    new_reminders =0 

    for proj in upcoming :

        existing =reminder_manager .get_pending_notifications ()
        already_exists =any (n ['project_id']==proj ['project_id']for n in existing )

        if not already_exists :
            reminder_manager .create_reminder_notification (
            proj ['project_id'],
            proj ['team_id'],
            proj ['hours_remaining'],
            proj ['time_remaining_str']
            )
            new_reminders +=1 
            print (f"  [OK] Created reminder for project: {proj ['project_id']}")

    if new_reminders ==0 :
        print ("  No new reminders needed")
    else :
        print (f"  Created {new_reminders } new reminder(s)")

    return new_reminders 

def show_employee_reminders (employee_id ):

    reminder_manager =ReminderNotificationManager ()

    displayed =reminder_manager .display_pending_reminders (employee_id )

    if not displayed :
        return 0 

    print ("\nWould you like to acknowledge these reminders?")
    print ("Note: Acknowledging means you've seen and noted the deadline")

    choice =input ("Acknowledge all? (y/n): ").strip ().lower ()

    if choice =='y':

        for notif_id in displayed :
            reminder_manager .acknowledge_notification (notif_id ,employee_id )
        print (f"\n[OK] Acknowledged {len (displayed )} reminder(s)")
    else :

        print ("\nAcknowledge specific reminders? Enter notification IDs (comma-separated) or 'skip':")
        response =input ("> ").strip ()

        if response .lower ()!='skip':
            notif_ids =[n .strip ()for n in response .split (',')]
            ack_count =0 

            for notif_id in notif_ids :
                if notif_id in displayed :
                    reminder_manager .acknowledge_notification (notif_id ,employee_id )
                    ack_count +=1 

            print (f"\n[OK] Acknowledged {ack_count } reminder(s)")

    return len (displayed )

if __name__ =="__main__":
    """
    Main execution - run the demonstration.
    """

    print ("\nTask Reminder System - Interactive Demo")
    print ("\nOptions:")
    print ("1. Run Full Demonstration")
    print ("2. Check and Create New Reminders")
    print ("3. Show Reminders for Specific Employee")
    print ("4. Exit")

    choice =input ("\nSelect option (1-4): ").strip ()

    if choice =='1':
        demonstrate_reminder_system ()

    elif choice =='2':
        check_and_create_reminders ()

    elif choice =='3':
        emp_id =input ("Enter Employee ID: ").strip ()
        count =show_employee_reminders (emp_id )
        if count ==0 :
            print (f"\nNo pending reminders for employee {emp_id }")

    elif choice =='4':
        print ("Exiting...")

    else :
        print ("Invalid option")
