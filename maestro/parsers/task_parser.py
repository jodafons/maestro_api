__all__ = ["task_parser"]


import glob, traceback, os, argparse, re, typing, pydantic

from tqdm import tqdm
from loguru import logger
from maestro.schemas import Job,Task
from maestro.standalone.job import test_job
from maestro.expand_folders import expand_folders
from maestro.client import maestro_client



def convert_string_to_range(s):
     """
       convert 0-2,20 to [0,1,2,20]
     """
     return sum((i if len(i) == 1 else list(range(i[0], i[1]+1))
                for i in ([int(j) for j in i if j] for i in
                re.findall(r'(\d+),?(?:-(\d+))?', s))), [])



class task_parser:

  def __init__(self , host, args=None):

    self.api = maestro_client(host, service = "pilot")
    if args:

      # Create Task
      create_parser = argparse.ArgumentParser(description = '', add_help = False)
      delete_parser = argparse.ArgumentParser(description = '', add_help = False)
      retry_parser  = argparse.ArgumentParser(description = '', add_help = False)
      list_parser   = argparse.ArgumentParser(description = '', add_help = False)


      create_parser.add_argument('-t','--task', action='store', dest='taskname', required=True,
                          help = "the task name to be append into the db.")
      create_parser.add_argument('-i','--inputfile', action='store',
                          dest='inputfile', required = True,
                          help = "the input config file that will be used to configure the job (sort and init).")
      create_parser.add_argument('--image', action='store', dest='image', required=False, default="",
                          help = "the singularity sif image path.")
      create_parser.add_argument('--exec', action='store', dest='command', required=True,
                          help = "the exec command")
      create_parser.add_argument('--dry_run', action='store_true', dest='dry_run', required=False, default=False,
                          help = "use this as debugger.")
      create_parser.add_argument('--do_test', action='store_true', dest='do_test', required=False, default=False,
                          help = "do local test")
      create_parser.add_argument('--token', action='store', dest='token', required=True,
                          help = "the user token.")
      create_parser.add_argument('--binds', action='store', dest='binds', required=False, default="{}",
                          help = "image volume bindd like {'/home':'/home','/mnt/host_volume:'/mnt/image_volume'}")
      create_parser.add_argument('-p','--partition', action='store', dest='partition', required=False, default="cpu",
                          help = "the cluster partition to run this task.")


      delete_parser.add_argument('--id', action='store', dest='id', required=True,
                    help = "All task ids to be deleted", type=str)
 
      retry_parser.add_argument('--id', action='store', dest='id', required=True,
                    help = "All task ids to be retried", type=str)

      kill_parser = argparse.ArgumentParser(description = '', add_help = False)
      kill_parser.add_argument('--id', action='store', dest='id', required=True, 
                    help = "All task ids to be killed", type=str)


      parent = argparse.ArgumentParser(description = '', add_help = False)
      subparser = parent.add_subparsers(dest='option')

      # Datasets
      subparser.add_parser('create', parents=[create_parser])
      subparser.add_parser('retry' , parents=[retry_parser])
      subparser.add_parser('delete', parents=[delete_parser])
      subparser.add_parser('list'  , parents=[list_parser])
      subparser.add_parser('kill'  , parents=[kill_parser])
      args.add_parser( 'task', parents=[parent] )

  

  def parser( self, args ):

    if args.mode == 'task':

      if args.option == 'create':
        self.create(os.getcwd(), args.taskname, args.inputfile,
                    args.image, args.command, args.token, dry_run=args.dry_run,
                    do_test=args.do_test, binds=args.binds, partition=args.partition)

      elif args.option == 'retry':
        self.retry(convert_string_to_range(args.id))
        
      elif args.option == 'delete':
        self.delete(convert_string_to_range(args.id))
        
      elif args.option == 'list':
        self.list()
        
      elif args.option == 'kill':
        self.kill(convert_string_to_range(args.id))
        
      else:
        logger.error("Option not available.")



  def create( self, basepath: str, 
                    taskname: str, 
                    inputfile: str,
                    image: str, 
                    command: str, 
                    email: str, 
                    dry_run: bool=False, 
                    do_test=True,
                    extension='.json', 
                    binds="{}", 
                    partition="cpu") -> bool:


    if ( not '%IN' in command):
      logger.error("the exec command must include '%IN' into the string. This will substitute to the configFile when start.")
      return False

    # task volume
    volume = basepath + '/' + taskname
    # create task volume
    if not dry_run:
      os.makedirs(volume, exist_ok=True)

    # check if input file is json
    input_files = expand_folders( inputfile )
    if len(input_files) == 0:
      logger.error(f"input files not found into {inputfile}.")
      return False
    else:
      logger.info(f"found {len(input_files)} into {inputfile}")

    jobs = []
    for job_id, input_file in tqdm( enumerate(input_files) ,  desc= 'creating... ', ncols=50):

        extension = input_file.split('/')[-1].split('.')[-1]
        workarea = volume +'/'+ input_file.split('/')[-1].replace('.'+extension, '')
        job = Job(
                      id=job_id,
                      image=image,
                      command=command.replace('%IN',input_file),
                      workarea=workarea,
                      inputfile=input_file,
                      envs=str({}),
                      binds=binds,
                      status='',
                      partition=partition
                    )
        jobs.append(job)


    task = Task( name = taskname, 
                 id   = -1,
                 volume = volume,
                 jobs = jobs,
                 partition = partition,
                 status = ''
                 )


    if do_test:
      logger.info("running my job locally for test...")
      if not test_job ( jobs[0] ):
        logger.error('local test failure. abort.')
        return False

    if not dry_run:
      if not self.api.ping():
        logger.error(f"service not available. please check your endpoint {self.api.host}")
        return False
      res = self.api.create(task)
      print(res)
      if res:
        logger.info(res[1])

    return True



  def kill(self, task_ids):
    for task_id in task_ids:
      logger.info(f"sending kill command for task {task_id} to the server...")
      res = self.api.kill(task_id)
      if res:
        logger.info(res[1])


  def delete(self, task_ids):
    for task_id in task_ids:
      logger.info(f"sending delete command for task {task_id} to the server...")
      res = self.api.delete(task_id)
      if res:
        logger.info(res[1])


  def retry(self, task_ids):
    for task_id in task_ids:
      logger.info(f"sending retry command for task {task_id} to the server...")
      res = self.api.retry(task_id)
      if res:
        logger.info(res[1])


  def list(self):
    print('not implemented')
  #  print(self.db.resume())


  













