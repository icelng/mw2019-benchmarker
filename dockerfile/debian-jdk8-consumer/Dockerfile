#runner container
FROM registry.cn-shanghai.aliyuncs.com/aliware2019/debian-jdk8-devel

#build adaptive-loadbalacne from user

COPY docker-entrypoint.sh /root/runtime/docker-entrypoint.sh

WORKDIR /root/workspace

ARG user_code_address

RUN set -ex && git clone --depth=1 -b  master $user_code_address && \
	cd adaptive-loadbalance && mvn clean install -Dmaven.test.skip=true && \
	cd /root/workspace && git clone --depth=1 -b master https://code.aliyun.com/middlewarerace2019/internal-service.git && \
	cd internal-service && mvn clean install -Dmaven.test.skip=true && \
	mkdir -p /root/dists && \
	cp /root/workspace/internal-service/service-consumer/target/service-consumer.jar /root/dists && \
	cp -b /root/workspace/adaptive-loadbalance/workspace-gateway/target/workspace-gateway-1.0.0.jar /root/dists/workspace-gateway.jar && \
	cp -b /root/workspace/adaptive-loadbalance/workspace-common/target/workspace-common-1.0.0.jar /root/dists/workspace-common.jar && \
        mkdir -p /root/runtime/logs && \
        cp /root/runtime/docker-entrypoint.sh /usr/local/bin && \
        chmod +x /usr/local/bin/docker-entrypoint.sh

RUN set -ex \
	&& mkdir -p /root/runtime/logs \
    && cp /root/runtime/docker-entrypoint.sh /usr/local/bin \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8087

ENTRYPOINT ["docker-entrypoint.sh"]

	

