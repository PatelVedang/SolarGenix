# Pull official base image
FROM kalilinux/kali-rolling

# Set work directory
WORKDIR /usr/src/app

# Update package lists and install necessary packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    python3 -m pip install --upgrade pip setuptools wheel

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system level tools
RUN apt-get install -y nikto nmap curl netcat-traditional wget

# Install dependencies
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

# Install SSLyze
RUN pip3 install sslyze

# Copy entrypoint.sh
COPY ./entrypoint.sh /usr/local/bin/
RUN sed -i 's/\r$//g' /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Copy project
COPY . .

# Run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
