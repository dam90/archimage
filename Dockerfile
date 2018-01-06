FROM centos:latest
# Install pip and git
RUN ["yum","-y","install","epel-release"]
RUN ["yum","-y","update"]
RUN ["yum","install","-y","python2-pip","git"]
# get the code
RUN ["git","clone","https://github.com/dam90/archimage"]
# install python dependencies
RUN ["cd","archimage"]
RUN ["pip","install","-r","requirements.txt"]
