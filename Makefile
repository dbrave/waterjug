setup:  
	docker build -t waterjug . ; docker run -p 5847:5847 waterjug:latest

test:
	./jugtests

