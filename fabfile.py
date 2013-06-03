from fabric.api import task, local, env, settings
from fabric.operations import put
import cuisine
from cuisine import run, sudo, package_ensure
import re
import socket
from server.config import get_settings_prod
import paramiko
from fabric.contrib.files import sed, append

PACKAGES_TO_INSTALL = [
    'libpq-dev',
    'python-dev',
    'nginx-extras',
    'python-virtualenv',
    'supervisor',
    'postgresql-9.1',
    'fail2ban',
    'vim',
    'tmux',
]

DD_API_KEY = '1234567890abcd'  # Datadog api key.
AWS_HOST = 'api.mobackapp.com'  # Amazon EC2 URL.
APP_NAME = 'moback'  # Name of the application.
USER_NAME = APP_NAME  # Username in which the app should be running.


# Say Hello
@task
def hello_world():
    '''Just a test task to test connecitvity'''
    run('echo "Hello World"')


# Vagrant
@task
def vagrant():
    '''Vagrant!'''
    host = '127.0.0.1'
    port = '2222'
    for line in local('vagrant ssh-config', capture=True).split('\n'):
        match = re.search(r'Hostname\s+(\S+)', line)
        if match:
            host = match.group(1)
            continue

        match = re.search(r'User\s+(\S+)', line)
        if match:
            env.user = match.group(1)
            continue

        match = re.search(r'Port\s+(\S+)', line)
        if match:
            port = match.group(1)
            continue

        match = re.search(r'IdentityFile\s(.+)', line)
        if match:
            env.key_filename = match.group(1)
            continue

    env.hosts = ['{0}:{1}'.format(host, port)]


@task
def aws():
    '''AWS config'''
    host = AWS_HOST
    port = 22
    env.hosts = ['{0}:{1}'.format(host, port)]
    env.user = 'ubuntu'
    env.key_filename = 'moback.pem'
    print 'HOST: ' + AWS_HOST


def update():
    """Update package list"""
    with settings(linewise=True, warn_only=True):
        sudo('apt-get -y update')


def upgrade():
    """Upgrade packages"""
    with settings(linewise=True, warn_only=True):
        sudo('aptitude -y upgrade')


def ensure_packages():
    for pkg in PACKAGES_TO_INSTALL:
        package_ensure(pkg)


def install_datadog():
    sudo('DD_API_KEY=%s bash -c "$(curl'
         ' -L http://dtdg.co/agent-install-ubuntu)"' % (DD_API_KEY, ))


def create_user():
    cuisine.user_ensure(
        USER_NAME, home='/home/%s' % USER_NAME, shell='/bin/bash')
    cuisine.group_user_ensure('www-data', USER_NAME)


def create_virtualenv():
    if not cuisine.dir_exists('/home/%s/ENV' % USER_NAME):
        sudo('virtualenv -q --distribute '
             '/home/%s/ENV' % (
             USER_NAME), user=USER_NAME)


def copy_source():
    '''archive the git source and copy it'''
    local('git archive $(git symbolic-ref HEAD 2>/dev/null)'
          ' | bzip2 > /tmp/%s.tar.bz2' % APP_NAME)
    remote_filename = '/tmp/%s.tar.bz2' % APP_NAME
    code_dir = '/home/%s/CODE' % APP_NAME
    sudo('rm -rf %s' % code_dir)
    if cuisine.file_exists(remote_filename):
        sudo('rm %s' % remote_filename)
    cuisine.file_upload(
        remote_filename, '/tmp/%s.tar.bz2' % APP_NAME)
    with cuisine.mode_sudo():
        run('mkdir -p %s' % code_dir)
        cuisine.file_attribs(remote_filename)
        run('tar jxf %s -C %s' % (remote_filename, code_dir))
        run('rm %s' % (remote_filename,))


def install_python_reqs():
    sudo('. /home/%s/ENV/bin/activate &&'
         ' pip install -r /home/%s/CODE/requirements.txt'
         % (USER_NAME, USER_NAME), user=USER_NAME)


def copy_confs():
    nginx_conf_path = '/etc/nginx/sites-available/default'
    sprvsr_conf_path = '/etc/supervisor/conf.d/moback.conf'
    pghba_path = '/etc/postgresql/9.1/main/pg_hba.conf'
    put('confs/nginx_default.conf',
        nginx_conf_path, True)
    put('confs/supervisord.conf', sprvsr_conf_path,
        True, mode=0644)
    put('confs/pg_hba.conf', pghba_path, True)
    with cuisine.mode_sudo():
        cuisine.file_attribs(
            nginx_conf_path, owner='root', group='root')
        cuisine.file_attribs(
            sprvsr_conf_path, owner='root', group='root')
        cuisine.file_attribs(
            pghba_path, owner='root', group='root')


def setup_db():
    cfg = get_settings_prod()
    dbname = cfg["db"]["database"]
    dbuser = cfg["db"]["username"]
    dbpasswd = cfg["db"]["password"]

    queries = [
        "psql -d postgres -c "
        "\"CREATE USER {dbuser} WITH PASSWORD"
        " '{dbpasswd}';\"",

        "psql -d postgres -c"
        " \"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL "
        "TABLES IN SCHEMA public TO {dbuser};\"",

        "psql -d postgres -c"
        " \"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA"
        " public TO {dbuser};\"",

        "psql -d postgres -c "
        "\"GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public"
        " TO {dbuser};\"",

        "psql -c \"CREATE DATABASE"
        " {dbname} WITH owner={dbuser};\"",
    ]
    for q in queries:
        try:
            query = q.format(dbuser=dbuser, dbpasswd=dbpasswd, dbname=dbname)
            sudo(query, user='postgres')
        except:
            pass
    try:
        sudo("psql -d moback -f /home/%s/CODE/extras/schema.sql" % USER_NAME,
             user='moback')
    except:
        pass


def reboot():
    sudo("shutdown -r 0")


def is_host_up(host, counter=0):
    print('%d : Attempting connection to host: %s' %
          (counter, host))
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(1)
    host_up = True
    try:
        paramiko.Transport((host, 22))
    except Exception, e:
        host_up = False
        print('%s down, %s' % (host, e))
    finally:
        socket.setdefaulttimeout(original_timeout)
        return host_up


def ping_untill_starts():
    counter = 0
    while not is_host_up(env.host, counter):
        counter += 1


@task
def restart_server():
    sudo('supervisorctl restart moback')


@task
def deploy_code():
    '''Deploy latest commit and restart uwsgi'''
    copy_source()
    restart_server()


@task
def configure_ebs():
    '''configure ebs volume for postgres befor executing this method
    sudo su -
    yes | mkfs -t ext3 /dev/xvdf
    mkdir /data
    mount /dev/xvdf /data
    '''

    with settings(warn_only=True):
        with cuisine.mode_sudo():
            run('service postgresql stop')
            run('rm -rf /data/lost+found')
            run('mkdir /data/lib/')
            run('mkdir /data/lib/PostgreSQL')
            run('mkdir /data/lib/PostgreSQL/9.1')
            run('mkdir /data/lib/PostgreSQL/9.1/main')
            run('cp -r /var/lib/postgresql/9.1/main /data/lib/PostgreSQL/9.1')
            run('chown -R postgres:postgres /data/lib/PostgreSQL')
            run('chmod 0700 /data/lib/PostgreSQL/9.1/main')
            run('touch /data/moback.log')
            run('chmod 777 /data/moback.log')

    append(
        '/etc/fstab',
        '/dev/xvdf   /data   ext3    defaults 0 0', use_sudo=True)
    sed('/etc/postgresql/9.1/main/postgresql.conf',
        '/var/lib/postgresql/9.1/main',
        '/data/lib/PostgreSQL/9.1/main',
        use_sudo=True)
    append(
        '/etc/postgresql/9.1/main/postgresql.conf',
        "listen_addresses = '*'", True)
    with settings(warn_only=True):
        with cuisine.mode_sudo():
            run('service postgresql start')
            run('service postgresql reload')


@task
def deploy_full(production='false'):
    '''Fresh and full deploy'''
    update()
    upgrade()
    ensure_packages()
    install_datadog()
    create_user()
    create_virtualenv()
    copy_source()
    install_python_reqs()
    copy_confs()
    setup_db()
    configure_ebs()
    restart_server()
    reboot()
    ping_untill_starts()


@task
def ssh():
    '''Open up ssh console'''
    try:
        if env.host == AWS_HOST:
            local('ssh -i moback.pem ubuntu@' + AWS_HOST)
    except:
        pass
