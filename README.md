* 支持在一台机器上测试，在同一台机器里运行4个Docker实例，并为其绑定相应的CPU(--cpuset-cpus)，因此单机最好有十个以上的CPU核心。

```
consumer: 0, 1, 2, 3 
provider-small: 4
provider-medium: 5, 6
provider-large: 7, 8, 9
```
* 把Docker实例的网络模式设置成host，consumer可通过Ip 0.0.0.0 访问到 small、medium以及large这三个实例。
* 修改Dockerfile,每次构建Docker镜像时都会拉取internal-service最新代码并编译打包成最新的Jar包 (因为我发现里边的Jar包有点旧了，并不是由最新代码打包的)
* 去掉包校验步骤，去掉日志打包步骤
* 目前Ncat镜像是阿里中间件内部的镜像，脚本中又没有镜像login的逻辑，因此暂时还不能拉取，所以把这个镜像的拉取给干掉，用系统namp中的ncat代替之。运行脚本之前得先安装nmap(目的是使用ncat判断端口是否被开启来确定实例启动是否成功)
```
# apt install nmap
（是的，我不知道在其它的平台怎么安装ncat）
```

# 2019阿里中间件性能挑战赛本地评测环境搭建指南

## 一、前期准备 

### 1.1 部分软件安装

以Mac为例，其他系统如 **CentOS** 使用 yum、**Ubuntu** 使用 apt 替代这里的 homebrew 即可

#### 1.1.1 安装 [Homebrew](https://brew.sh/)

```bash
$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

#### 1.1.2 安装 Python 3

```bash
$ brew install python
```

**注：最新版的 Homebrew 运行 `brew install python` 命令会默认安装 Python 3。**

#### 1.1.3 安装 [Pipenv](https://docs.pipenv.org/)

```bash
$ brew install pipenv
```

#### 1.1.4 克隆本代码仓库

```bash
$ git clone https://github.com/yiranFancier/mw2019-benchmarker.git ~/benchmarker
```

#### 1.1.5 创建 Python 运行环境

```bash
$ cd ~/benchmarker/workflow
$ pipenv install
```

#### 1.1.6 安装 wrk

```bash
$ brew install wrk
```

#### 1.1.7 安装 Docker

```bash
$ brew install docker
```
虽然 Docker 可以以非 root 身份运行，但是本脚本并没有采用这样的运行方式，因此需要使用 `sudo` 运行 `docker` 命令。且我们默认执行 `sudo` 命令的时候是需要输入密码的，因此要在当前用户的 `home` 目录下创建一个 `.passwd` 文件，里面包含 `sudo` 命令所需要使用的密码，例>如：

```
!@#qweASD
<此处应有一个空行>
```

**注：密码后面需要跟随一个回车换行，详细说明请参考 `man sudo`。**

#### 1.8 配置免密 SSH 登录

在配置文件 bootstrap.conf 文件中 REMOTE 下修改 Provider、Consumer主机相关配置，包括主机名、端口与IP地址。

因程序启动时端口已限定，因此建议维持配置文件中端口的值，将主机名、IP地址修改为相应云主机或虚拟机的主机名与IP地址即可。

这里的主机名主要用于方便识别机器，如该程序把 provider-small、provider-medium、provider-large 分别部署于 sm01、md01、lg01主机上，如不需要该特性，主机名设置为IP地址即可。

该程序连接远程主机时使用免密的方式，因此需要提前配置免密登录，配置方式参考：[SSH免密登录配置](https://buzheng.org/linux/how-to-setup-passwordless-ssh-login/)

### 1.2 开始压测

#### 1.2.1 设置自己 adaptive_loadbalance 的代码 git 地址
本评测程序会自动从 git 代码库拉取 adaptive_loadbalance 的代码，默认的是官方提供的代码，选手可在 bootstrap.conf 中，修改 **DefaultCodeAddress** 地址为自己的代码库 git 地址即可。

#### 1.2.2 启动 mock server

```bash
$ cd ~/benchmarker
$ python3 mock/server.py
```

### 1.2.3 启动bootstrap.py
重新开启一个窗口，执行如下命令
```bash
$ cd ~/bencmarker/workflow
$ python3 bootstrap.py
```
至此，整个评测流程已开始，选手可以通过窗口日志查看qps等信息。
