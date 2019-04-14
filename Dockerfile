FROM python:3
USER root
RUN mkdir -p /opt/waterjug
RUN mkdir -p /opt/waterjug/templates
RUN pip install flask

ADD waterjug.py /opt/waterjug/waterjug.py
ADD templates/* /opt/waterjug/templates/
WORKDIR /opt/waterjug
CMD [ "python", "/opt/waterjug/waterjug.py" ]
