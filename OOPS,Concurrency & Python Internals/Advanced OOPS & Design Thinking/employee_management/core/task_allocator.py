import sys 
import os 
sys .path .append (os .path .dirname (os .path .dirname (os .path .abspath (__file__ ))))
from utils .json_handler import JSONHandler 

class TaskAllocator :

    def __init__ (self ):
        pass 

    def allocate_project_to_team (self ,project_obj ,requester_employee ):
        if not requester_employee .can_allocate_tasks ():
            raise PermissionError ('Only CTO can allocate tasks')
        teams_data =JSONHandler .load ('teams.json')
        if not teams_data :
            return False 
        suitable_teams =[]
        for team_id ,team_data in teams_data .items ():
            if team_data .get ('department','').lower ()!=project_obj .department .lower ():
                continue 
            members_count =1 +len (team_data .get ('members',[]))
            if members_count >6 :
                continue 
            team_level =team_data .get ('level',2 )
            if team_level >=project_obj .difficulty :
                suitable_teams .append ((team_id ,team_data ,team_level ))
        if not suitable_teams :
            return False 
        suitable_teams .sort (key =lambda x :x [2 ],reverse =True )
        best_team_id ,best_team_data ,best_team_level =suitable_teams [0 ]
        project_obj .assigned_team_id =best_team_id 
        project_obj .status ='in-progress'
        project_obj .update ()
        return True 

    def allocate_all_pending_projects (self ,requester_employee ):
        if not requester_employee .can_allocate_tasks ():
            raise PermissionError ('Only CTO can allocate tasks')
        from core .project import Project 
        projects_data =JSONHandler .load ('projects.json')
        pending_projects =[Project .from_dict (p )for p in projects_data .values ()if p .get ('status')=='pending']
        if not pending_projects :
            return 
        allocated_count =0 
        for project in pending_projects :
            if self .allocate_project_to_team (project ,requester_employee ):
                allocated_count +=1 

    def get_team_workload (self ,team_id ):
        projects_data =JSONHandler .load ('projects.json')
        team_projects =[p for p in projects_data .values ()if p .get ('assigned_team_id')==team_id ]
        return team_projects 

    def get_unassigned_projects (self ):
        projects_data =JSONHandler .load ('projects.json')
        from core .project import Project 
        unassigned =[Project .from_dict (p )for p in projects_data .values ()if not p .get ('assigned_team_id')]
        return unassigned 

    def print_allocation_summary (self ):
        projects_data =JSONHandler .load ('projects.json')
        teams_data =JSONHandler .load ('teams.json')
        team_assignments ={}
        unassigned =[]
        for proj_data in projects_data .values ():
            team_id =proj_data .get ('assigned_team_id')
            if team_id :
                if team_id not in team_assignments :
                    team_assignments [team_id ]=[]
                team_assignments [team_id ].append (proj_data )
            else :
                unassigned .append (proj_data )
