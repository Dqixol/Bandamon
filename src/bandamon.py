import argparse
import datetime
import json
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen
import os
import time
import datetime

cols_of_interest = [
    'jeditaskid',
    'status',
    'taskname',
    # 'username',
    # 'creationdate',
    # 'modificationtime',
    # 'reqid',
    # 'oldstatus',
    # 'cloud',
    # 'site',
    'starttime',
    'endtime',
    # 'frozentime',
    # 'prodsourcelabel',
    # 'workinggroup',
    # 'vo',
    # 'corecount',
    # 'tasktype',
    # 'processingtype',
    # 'taskpriority',
    # 'currentpriority',
    # 'architecture',
    # 'transuses',
    # 'transhome',
    # 'transpath',
    # 'lockedby',
    # 'lockedtime',
    # 'termcondition',
    # 'splitrule',
    # 'walltime',
    # 'walltimeunit',
    # 'outdiskcount',
    # 'outdiskunit',
    # 'workdiskcount',
    # 'workdiskunit',
    'ramcount',
    # 'ramunit',
    # 'iointensity',
    # 'iointensityunit',
    # 'workqueue_id',
    # 'progress',
    # 'failurerate',
    # 'errordialog',
    # 'countrygroup',
    # 'parent_tid',
    # 'eventservice',
    # 'ticketid',
    # 'ticketsystemtype',
    # 'statechangetime',
    # 'superstatus',
    # 'campaign',
    # 'gshare',
    'cputime',
    'cputimeunit',
    # 'basewalltime',
    # 'cpuefficiency',
    # 'nucleus',
    # 'ttcrequested',
    # 'ttcpredicted',
    # 'ttcpredictiondate',
    # 'resquetime',
    # 'requesttype',
    # 'resourcetype',
    # 'usejumbo',
    # 'diskio',
    # 'diskiounit',
    # 'container_name',
    # 'attemptnr',
    'age',
    'duration_days',
    # 'owner',
    # 'category',
    # 'totevrem',
    # 'dsinfo',
    'nfiles',
    'nfilesfinished',
    'nfilesfailed',
    'nfilesmissing',
    'pctfinished',
    # 'pctfailed',
    # 'neventsTot',
    # 'neventsUsedTot',
    # 'neventsOutput',
    # 'totev',
    # 'datasets',
    # 'scoutinghascritfailures',
    # 'datasetid',
    # 'datasetname',
    # 'type',
    # 'creationtime',
    # 'masterid',
    # 'provenanceid',
    # 'containername',
    # 'state',
    # 'statechecktime',
    # 'statecheckexpiration',
    # 'nfilestobeused',
    # 'nfilesused',
    # 'nevents',
    # 'neventstobeused',
    # 'neventsused',
    # 'attributes',
    # 'streamname',
    # 'storagetoken',
    # 'destination',
    # 'nfilesonhold',
    # 'templateid',
    # 'nfileswaiting',          
]

class bcolors:
    RED = '\033[0;91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'

color_dic = {
    'running': bcolors.BLUE + bcolors.BOLD,
    'submitting': bcolors.CYAN,
    'registered': bcolors.MAGENTA,
    'ready': bcolors.MAGENTA,
    'done': bcolors.GREEN,
    'finished': bcolors.YELLOW,
    'broken': bcolors.RED + bcolors.BOLD,
    'aborted': bcolors.RED,
    'failed': bcolors.RED,
    'scouting': '',
    'scouted': '',
}

def get_tasks(taskname = 'user.emusk', user = 'emusk', days=None, do_json=True, force=False, metadata=False):
    _headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    pars = {'taskname': taskname + '*', 'datasets': True, 'limit': 10000}
    if metadata:
        pars['extra'] = 'metastruct'
    if user:
        pars['username'] = user
    if do_json:
        pars['json'] = 1
    if force:
        pars['timestamp'] = datetime.datetime.utcnow().strftime('%H:%M:%S')
    if days is not None:
        pars['days'] = days
    url = 'https://bigpanda.cern.ch/tasks/?' + urlencode(pars)
    req =  Request(url, headers=_headers)
    reply = None
    while reply is None:
        try:
            reply = urlopen(req).read().decode('utf-8')
        except Exception:
            pass

    datasets = json.loads(reply)
    return datasets, time.time()

def get_jobs(taskid):
    url = f'https://bigpanda.cern.ch/jobs/?jeditaskid={taskid}&json=1'
    req =  Request(url)
    reply = urlopen(req).read().decode('utf-8')
    datasets = json.loads(reply)
    return datasets

def printAllInfo(line, n_col=120):
    eta = line["duration_days"] * 24 / (line["nfilesfinished"] / line["nfiles"]) - line["duration_days"] * 24 if line["nfilesfinished"] > 0 else float('inf')
    overall_color = color_dic.get(line["status"], "") if line["status"] != "running" else (bcolors.BLUE if line["nfilesfailed"] == 0 else bcolors.YELLOW)
    status = str(line["status"]).ljust(10)
    numbers = f'{str(line["nfilesfinished"]).rjust(4)} / {str(line["nfiles_left"]).rjust(4)} / {str(line["nfilesfailed"]).rjust(4)} ({str(int(line["pctfinished"])).rjust(2)}%)'.rjust(30)
    duration = f'{round(line["duration_days"] * 24, 1)}/{round(eta, 1)} hrs'.rjust(15," ")
    part_status = f'{overall_color}{status}{bcolors.ENDC}'
    part_id     = f'{overall_color}{line["jeditaskid"]}{bcolors.ENDC}'
    part_numbers = f'{overall_color}{bcolors.BOLD}{numbers}{bcolors.ENDC}'.ljust(20," ")
    part_name = f'{overall_color}{line["taskname"]}'
    part_duration = f'{overall_color}{duration}{bcolors.ENDC}'
    final_expr =     f'{part_status} {part_id           } {part_duration} {part_numbers}   {part_name}'
    final_expr_raw = f'{status     } {line["jeditaskid"]} {duration     } {numbers     }   {line["taskname"]}'
    if len(final_expr_raw) >= n_col:
        extra = len(final_expr_raw) - n_col
        final_expr = final_expr[:-extra-3] + '...'
    print(final_expr)

def printIssueInfo(line, do_details):
    overall_color = bcolors.YELLOW
    status = str(line["status"]).ljust(10)
    part_one = f'{overall_color}WARNING:{bcolors.ENDC}'
    part_two = f'{color_dic.get(line["status"], "")}{status}{bcolors.ENDC}'
    part_three = f'{bcolors.YELLOW}task {line["jeditaskid"]} have {str(line["nfilesfailed"])} failed files, retry at{bcolors.ENDC}'
    part_four = f'{bcolors.YELLOW}{bcolors.UNDERLINE}https://prodtask-dev.cern.ch/ng/task/{line["jeditaskid"]}{bcolors.ENDC}'
    print(f'{part_one} {part_two} {part_three} {part_four}')
    if do_details:
        job_details = get_jobs(str(line["jeditaskid"]))
        print(f'{bcolors.YELLOW}\tJobs summary:{bcolors.ENDC}')
        for entry in job_details.get('selectionsummary'):
            if entry.get('field') == 'jobstatus':
                [print(f'{bcolors.YELLOW}\t\t', dict['kname'], '\t', dict['kvalue'], bcolors.ENDC) for dict in entry.get('list')]

        job_error_df = job_details.get('errsByCount')
        print(f'{bcolors.YELLOW}\tJobs errors:{bcolors.ENDC}')
        for errdict in job_error_df:
            print(f'\t\t{bcolors.YELLOW}', len(errdict), errdict.get('diag'), bcolors.ENDC)
        print('')


def heavyLifting(user, expressions, inverses, do_details, past_list, show_done=False, print_all = False):
    df, ts = get_tasks(taskname = user, user = '', days=None, do_json=True, force=False, metadata=False)
    if len(df) == 0:
        print(f'{bcolors.YELLOW}WARNING: No task found, sure you have task submitted?')
        exit()
    df_of_interest = []
    for line in df:
        for expression in expressions:
            if expression in line['taskname']:
                df_of_interest.append(line)
        for expression in inverses:
            if expression in line['taskname']:
                df_of_interest.remove(line)
    if len(df_of_interest) == 0:
        print(f'{bcolors.YELLOW}WARNING: No task found, change your selection!')
        exit()
    for line in df_of_interest:
        line['nfiles_left'] = line['nfiles'] - line['nfilesfinished']
    df_of_interest = sorted(df_of_interest, key=lambda x: (x['nfilesfailed'], x['nfiles_left']),reverse=True)
    df_issue = [line for line in df_of_interest if line['nfilesfailed'] != 0]
    nfiles_total = sum([line['nfiles'] for line in df_of_interest])
    nfiles_done  = sum([line['nfilesfinished'] for line in df_of_interest])
    past_list.append((ts, nfiles_done))
    while time.time() - past_list[0][0] > 3600:
        past_list.pop(0)
    avg_age = sum([line['age'] for line in df_of_interest]) / len(df_of_interest)
    eta = (avg_age * 24 / (nfiles_done / nfiles_total)  - (avg_age * 24)) if nfiles_done > 0 else float('inf')
    nfiles_done_past_hour = (past_list[-1][1] - past_list[0][1])
    time_past_hour = (past_list[-1][0] - past_list[0][0]) / 60
    os.system('clear')
    n_col = os.get_terminal_size().columns
    n_line = os.get_terminal_size().lines
    print(f'status     id      elapsed/estimate      done / left / fail    (%)   name')
    print(f'-'*(n_col))
    if len(df_of_interest) > 0:
        n_to_print = n_line - 16 - len(df_issue)
        n_printed = 0
        if show_done:
            for line in df_of_interest:
                printAllInfo(line, n_col)
                n_printed += 1
                if not print_all:
                    if n_printed >= n_to_print:
                        print(f"{bcolors.ENDC}......")
                        break
        else:
            for line in df_of_interest:
                if line['status'] != 'done':
                    printAllInfo(line, n_col)
                    n_printed += 1
                    if not print_all:
                        if  n_printed >= n_to_print:
                            print(f"{bcolors.ENDC}......")
                            break
    else:
        print(f'{bcolors.YELLOW}WARNING: No job found, change your selection!')
        exit()
    print(f'-'*(n_col))

    if len(df_issue) > 0:
        print(f'\n')
        for line in df_issue:
            printIssueInfo(line, do_details)
        retry_ids = [str(line["jeditaskid"]) for line in df_issue if line["status"] != "broken"]
        print(f'\n{bcolors.YELLOW}Retry by `pbook retry {",".join(retry_ids)}`')
    print(f'\n')
    print (f'{bcolors.GREEN}INFO: Overall progress {nfiles_done} / {nfiles_total} ({round(100*(nfiles_done/nfiles_total), 2)}%) files, {nfiles_total-nfiles_done} left, elapse {round(avg_age * 24,1)} hours, eta {round(eta,1)} hours{bcolors.ENDC}')
    if nfiles_done_past_hour > 0:
        ins_eta = (nfiles_total - nfiles_done) /  (time_past_hour / 60 / nfiles_done_past_hour)
        print (f'{bcolors.GREEN}INFO: In the past {round(time_past_hour, 1)} mins, {nfiles_done_past_hour} files were processed, inst. eta {round(ins_eta,1)} hours')
    print (f'\n{bcolors.GREEN}INFO: Go to {bcolors.UNDERLINE}https://bigpanda.cern.ch/user/{bcolors.ENDC}{bcolors.GREEN} for more info{bcolors.ENDC}')
    now  = datetime.datetime.now()
    print (f'{bcolors.GREEN}INFO: Updated {datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")}{bcolors.ENDC}') 
    return past_list;


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--expressions', nargs='+', default=[])
    parser.add_argument('-v', '--inverses', nargs='+', default=[])
    parser.add_argument("-u", '--user', help="User interested", type=str)
    parser.add_argument("-d", '--detail', help="show job details", action="store_true")
    parser.add_argument("-l", '--loop', help="None stop monitoring", action="store_true")
    parser.add_argument("-s", '--show_done', help="show done jobs", action="store_true")
    parser.add_argument("-a", '--print_all', help="show all", action="store_true")
    args = parser.parse_args()
    user = f'user.{os.getlogin()}' if not args.user else f'user.{args.user}'
    show_done = args.show_done if args.show_done else False
    a_list = []
    while True:
        detail = args.detail if args.detail else False
        a_list = heavyLifting(user=user, expressions=args.expressions, inverses=args.inverses, do_details=args.detail, past_list=a_list, show_done=show_done, print_all = args.print_all)
        if not args.loop:
            break
        time.sleep(60)
        

