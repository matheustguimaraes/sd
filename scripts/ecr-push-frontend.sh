cd frontend
echo "Building frontend..."
docker build -t mdcc-nuvem-frontend .
echo "Tagging frontend..."
docker tag mdcc-nuvem-frontend:latest 948532068149.dkr.ecr.us-east-1.amazonaws.com/mdcc-nuvem-frontend:latest
echo "Pushing frontend..."
docker push 948532068149.dkr.ecr.us-east-1.amazonaws.com/mdcc-nuvem-frontend:latest
echo "Frontend built and pushed successfully!"
