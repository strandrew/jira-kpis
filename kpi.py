#!/bin/python
from __future__ import print_function
from jira import JIRA
from pyfiglet import figlet_format
import datetime

def all_issues_from_query(query):
	done = False
	start = 0
	total = 0
	all_issues = []
	while not done:
		issues = jira.search_issues(query, start)
		all_issues += issues
		#print('not done len(issues): {} total: {} start: {}'.format(len(issues), total, start))
		total += len(issues)
		start += len(issues)
		if (len(issues) == 0):
			done = True

	return all_issues

def all_opened_bugs_before_start_of_year():
	"""Retrieves all open bugs before the start of the current year"""
	now = datetime.datetime.now()
	query = 'issuetype = Bug and created < {}-01-01 and status in (open, reopened) and priority > minor'.format(now.year)
	all_issues = all_issues_from_query(query)
	return all_issues

def all_closed_critical_bugs_before_start_of_year():
	"""Retrieves all closed critical bugs before the start of the current year"""
	now = datettime.datetime.now()
	query = 'issuetype = Bug and created < {}-01-01 and status not in (open, reopened) and priority = critical'.format(now.year)

def calculate_average_age(all_issues):
	now = datetime.datetime.now()

	total_days_open = 0
	
	for issue in all_issues:
		issue_date = datetime.datetime.strptime(issue.fields.created[:19], '%Y-%m-%dT%H:%M:%S')
		days_open = (now-issue_date).days
		#print('jira field: {} - python date: {} - days old: {}'.format(issue.fields.created, issue_date, days_open))
		total_days_open += days_open
	
	return (total_days_open/len(all_issues))

def calculate_average_days_open(monthly_issues):

	total_days_open = 0

	for issue in monthly_issues:
		open_date = datetime.datetime.strptime(issue.fields.created[:19], '%Y-%m-%dT%H:%M:%S')
		close_date = datetime.datetime.strptime(issue.fields.resolutiondate[:19], '%Y-%m-%dT%H:%M:%S')
		days_open = (close_date-open_date).days
		total_days_open += days_open

	if (len(monthly_issues) == 0):
		return 0
	else:	
		return (total_days_open/len(monthly_issues))

def print_header_row():
	now = datetime.datetime.now()

	print(',', end='')
	for i in range(1, 13):
		tmpDate = datetime.datetime(now.year, i, 1)
		print('{}'.format(tmpDate.strftime('%B')), end='')
		if (i < 12):
			print(',', end='')
		else:
			print('')
	return

def print_average_ages():
	now = datetime.datetime.now()
	averageString = 'Running average age of elevated priority bugs'
	all_issues = all_opened_bugs_before_start_of_year()

	# loop through all months
	for i in range(1, 13):
		i2 = i+1
		y = now.year
		y2 = y
	
		if (i2 > 12):
			i2 = 1
			y2 += 1

		query = 'issuetype = Bug and created  >= "{}-{}-01" and created < "{}-{}-01" and status in (open, reopened) and priority > minor'.format(y, i, y2, i2)
		all_issues += all_issues_from_query(query)
		averageString += ', {}'.format(calculate_average_age(all_issues))


	print(averageString)


	return

def print_average_time_to_close_critical_bugs():
	now = datetime.datetime.now()
	averageString = 'Average time in days to close critical bugs per month'

	# loop through all months
	for i in range(1, 13):
		i2 = i+1
		y = now.year
		y2 = y
	
		if (i2 > 12):
			i2 = 1
			y2 += 1

		query = 'issuetype = Bug and created  >= "{}-{}-01" and created < "{}-{}-01" and status not in (open, reopened) and priority = critical'.format(y, i, y2, i2)
		monthly_issues = all_issues_from_query(query)
		averageString += ', {}'.format(calculate_average_days_open(monthly_issues))

	print(averageString)

	return

def simple_count_query(query):
	# loop through all months
	now = datetime.datetime.now()
	lineString = ''
	for i in range(1, 13):
		i2 = i+1
		y = now.year
		y2 = y
	
		if (i2 > 12):
			i2 = 1
			y2 += 1

		queryToExec = query.format(y, i, y2, i2)
		monthly_issues = all_issues_from_query(queryToExec)
		lineString += ', {}'.format(len(monthly_issues))

	return lineString

def print_support_issues_escalated_per_month():

	lineString = 'Number of support issues escalated per month'
	query = 'project = SUPPORT and issuetype = Task and created  >= "{}-{}-01" and created < "{}-{}-01"'
	lineString += simple_count_query(query)

	print(lineString)
	return

def print_enhancements_released_per_month():
	lineString = 'Enhancements released per month'
	query = 'issuetype in ("New Feature", "Improvement") and resolved  >= "{}-{}-01" and resolved < "{}-{}-01"'
	lineString += simple_count_query(query)

	print(lineString)
	return

def print_bugs_released_per_month():
	lineString = 'Bugs released per month'
	query = 'issuetype = Bug and resolved  >= "{}-{}-01" and resolved < "{}-{}-01"'
	lineString += simple_count_query(query)

	print(lineString)
	return

def print_bugs_reported_per_month():
	lineString = 'Bugs reported per month (all priorities)'
	query = 'issuetype = Bug and created  >= "{}-{}-01" and created < "{}-{}-01"'
	lineString += simple_count_query(query)

	print(lineString)
	return	

def print_releases_per_month():
	now = datetime.datetime.now()
	lineString = 'Releases per month'
	releases_per_month = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

	all_projects = jira.projects()
	for project in all_projects:
		releases = jira.project_versions(project.key)
		for release in releases:
			isRelease = release.name[-1:].isdigit()
			isNotPatch = (release.name.find('RUP') == -1)
		
			if (release.released == True and isRelease and isNotPatch):
				release_date = datetime.datetime.strptime(release.releaseDate, '%Y-%m-%d')
				if (release_date.year == now.year):
					releases_per_month[release_date.month-1] += 1
					print('DEBUG: Project: {} - Version: {} - Date: {}'.format(project.key, release.name, release_date))


	for totalInMonth in releases_per_month:
		lineString += ', {}'.format(totalInMonth)

	print(lineString)
	return	
####################################################################################################################
""" Calculate my KPIs """
# first thing is to connect to JIRA
options = {
    'server': 'http://jira.strsoftware.com'
}

jira = JIRA(options)


print_header_row()
print_average_ages()
print_average_time_to_close_critical_bugs()
print_support_issues_escalated_per_month()
print_enhancements_released_per_month()
print_bugs_released_per_month()
print_bugs_reported_per_month()
print_releases_per_month()

