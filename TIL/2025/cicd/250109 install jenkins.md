
### GCP로 debian 서버를 만들고 젠킨스 띄우기

1. GCP에 서버 띄우기
2. 구글 클라우드 서버를 ssh로 접속 
	- sudo passwd : 패스워드 설정
3. Java 설치 17.0.13
```bash
sudo apt update
sudo apt install fontconfig openjdk-17-jre
java -version
openjdk version "17.0.13" 2024-10-15
OpenJDK Runtime Environment (build 17.0.13+11-Debian-2)
OpenJDK 64-Bit Server VM (build 17.0.13+11-Debian-2, mixed mode, sharing)
```
4. Debian 서버 Long Term Support release 설치
```bash
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc]" \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins
```
5. jenkins 실행하기
```bash
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins
```
6. 방화벽 설정 (8080 포트 열어주기)
	- gcp 콘솔에서 추가하기
### Jenkins GUI 창 접속 후
- 비밀번호 확인
	- `sudo cat /var/lib/jenkins/secrets/initialAdminPassword`
- 제안 플러그인 설치
- 관리자 사용자 만들기 및 설정
