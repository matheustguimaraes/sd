# Autenticar no ECR antes de fazer push
echo "Authenticating to ECR..."
aws ecr --profile matheus.tg get-login-password --region us-east-1 | docker login --username AWS --password-stdin 948532068149.dkr.ecr.us-east-1.amazonaws.com

cd frontend
echo "Building frontend..."
docker build --platform=linux/amd64 -t mdcc-nuvem-frontend .
echo "Tagging frontend..."
docker tag mdcc-nuvem-frontend:latest 948532068149.dkr.ecr.us-east-1.amazonaws.com/mdcc-nuvem-frontend:latest
echo "Pushing frontend..."
docker push 948532068149.dkr.ecr.us-east-1.amazonaws.com/mdcc-nuvem-frontend:latest
echo "Frontend built and pushed successfully!"
