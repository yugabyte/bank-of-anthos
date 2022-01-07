FROM openjdk:11-jre-slim
VOLUME /tmp
COPY target/ledgerwriter-1.0.jar app.jar
ENV JAVA_OPTS=""
ENTRYPOINT exec java -jar /app.jar
