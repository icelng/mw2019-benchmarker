#runner container
FROM registry.cn-shanghai.aliyuncs.com/aliware2019/debian-jdk8-devel

#build adaptive-loadbalacne from user

COPY docker-entrypoint.sh /root/runtime/docker-entrypoint.sh

WORKDIR /root/workspace

ARG user_code_address

RUN set -ex && git clone --depth=1 -b  master $user_code_address && \
	cd adaptive-loadbalance && mvn clean install -Dmaven.test.skip=true && \
	mkdir -p /root/dists && \
	cp /root/workspace/services/internal-service/service-provider/target/service-provider.jar /root/dists && \
	cp -b /root/workspace/adaptive-loadbalance/workspace-provider/target/workspace-provider-1.0.0.jar /root/dists/workspace-provider.jar && \
	cp -b /root/workspace/adaptive-loadbalance/workspace-common/target/workspace-common-1.0.0.jar /root/dists/workspace-common.jar && \
        mkdir -p /root/runtime/logs && \
        cp /root/runtime/docker-entrypoint.sh /usr/local/bin && \
        chmod +x /usr/local/bin/docker-entrypoint.sh

RUN set -ex \
	&& mkdir -p /root/runtime/logs \
    && cp /root/runtime/docker-entrypoint.sh /usr/local/bin \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 20880

ENTRYPOINT ["docker-entrypoint.sh"]

	

