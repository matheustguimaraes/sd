cd backend
echo "Building backend..."
docker build -t mdcc-nuvem-backend .
echo "Tagging backend..."
docker tag mdcc-nuvem-backend:latest 948532068149.dkr.ecr.us-east-1.amazonaws.com/mdcc-nuvem-backend:latest
echo "Pushing backend..."
docker push 948532068149.dkr.ecr.us-east-1.amazonaws.com/mdcc-nuvem-backend:latest
echo "Backend built and pushed successfully!"

echo "Tagging worker..."
docker tag mdcc-nuvem-backend:latest 948532068149.dkr.ecr.us-east-1.amazonaws.com/mdcc-nuvem-worker:latest
echo "Pushing worker..."
docker push 948532068149.dkr.ecr.us-east-1.amazonaws.com/mdcc-nuvem-worker:latest
echo "Worker built and pushed successfully!"
