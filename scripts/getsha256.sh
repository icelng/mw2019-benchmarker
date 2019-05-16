providerImage=registry.cn-shanghai.aliyuncs.com/aliware2019/provider
consumerImage=registry.cn-shanghai.aliyuncs.com/aliware2019/consumer

docker pull $providerImage
docker pull $consumerImage

line1="ProviderAppSha256 = "
line2=$(docker run --rm -i --entrypoint='' $providerImage bash -c 'sha256sum /root/dists/service-provider.jar')
echo $line1$line2 >> sha256.txt

line1="ConsumerAppSha256  = "
line2=$(docker run --rm -i --entrypoint='' $consumerImage bash -c 'sha256sum /root/dists/service-consumer.jar')
echo $line1$line2 >> sha256.txt

line1="ProviderScriptSha256  = "
line2=$(docker run --rm -i --entrypoint='' $providerImage bash -c 'sha256sum /root/runtime/docker-entrypoint.sh')
echo $line1$line2 >> sha256.txt

line1="ConsumerScriptSha256 = "
line2=$(docker run --rm -i --entrypoint='' $consumerImage bash -c 'sha256sum /root/runtime/docker-entrypoint.sh') 
echo $line1$line2 >> sha256.txt
