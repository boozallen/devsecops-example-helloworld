FROM frolvlad/alpine-oraclejdk8:slim
VOLUME /tmp
ADD webapp/target/spring-boot-web-jsp-1.0.war app.war
RUN sh -c 'touch /app.war'
ENTRYPOINT ["java","-jar","/app.war"]