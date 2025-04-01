import React, { useState } from "react";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  useToast,
  Select,
  Checkbox,
  HStack,
  Progress,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Card,
  CardBody,
  CardHeader,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const RepositoryAnalysis = () => {
  const [githubUrl, setGithubUrl] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [reportFormat, setReportFormat] = useState("html");
  const [includeBenchmarks, setIncludeBenchmarks] = useState(true);
  const [includeSuggestions, setIncludeSuggestions] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [repositories, setRepositories] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState("");

  const toast = useToast();
  const navigate = useNavigate();

  const parseGitHubUrl = (url) => {
    try {
      const regex = /github\.com\/([^/]+)\/([^/]+)/;
      const match = url.match(regex);
      if (match && match.length >= 3) {
        return {
          owner: match[1],
          repo: match[2].replace(".git", ""),
        };
      }
      return null;
    } catch (error) {
      return null;
    }
  };

  const fetchRepositories = async () => {
    if (!accessToken) {
      setError("GitHub access token is required");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await axios.get("http://localhost:8000/api/github/repositories", {
        params: { access_token: accessToken },
      });

      setRepositories(response.data);

      toast({
        title: "Repositories fetched",
        description: `Found ${response.data.length} repositories`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      setError(error.response?.data?.detail || "Error fetching repositories");
      toast({
        title: "Error",
        description:
          error.response?.data?.detail || "Failed to fetch repositories",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const startAnalysis = async () => {
    setError("");
    setIsLoading(true);
    setProgress(0);

    let owner, repo;

    if (selectedRepo) {
      const [repoOwner, repoName] = selectedRepo.split("/");
      owner = repoOwner;
      repo = repoName;
    } else {
      const parsed = parseGitHubUrl(githubUrl);
      if (!parsed) {
        setError(
          "Invalid GitHub URL format. Please use a URL like https://github.com/owner/repo"
        );
        setIsLoading(false);
        return;
      }
      owner = parsed.owner;
      repo = parsed.repo;
    }

    if (!accessToken) {
      setError("GitHub access token is required");
      setIsLoading(false);
      return;
    }

    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        const newProgress = prev + (100 - prev) * 0.1;
        return newProgress >= 95 ? 95 : newProgress;
      });
    }, 1000);

    try {
      // FIXME: use env variable for API URL
      
      const response = await axios.post("http://localhost:8000/api/report/generate", {
        owner,
        repo,
        access_token: accessToken,
        company_name: companyName || undefined,
        include_benchmarks: includeBenchmarks,
        include_suggestions: includeSuggestions,
        format: reportFormat,
      });

      clearInterval(progressInterval);
      setProgress(100);

      toast({
        title: "Analysis Complete",
        description: "Repository analysis and report generation successful",
        status: "success",
        duration: 5000,
        isClosable: true,
      });

      setTimeout(() => {
        navigate("/reports");
      }, 1500);
    } catch (error) {
      clearInterval(progressInterval);
      setProgress(0);
      setError(error.response?.data?.detail || "Error during analysis");

      toast({
        title: "Analysis Failed",
        description: error.response?.data?.detail || "Error during analysis",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box maxW="800px" mx="auto">
      <Heading mb={6}>Repository Analysis</Heading>

      <Card mb={6}>
        <CardHeader>
          <Heading size="md">GitHub Authentication</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <FormControl isRequired>
              <FormLabel>GitHub Personal Access Token</FormLabel>
              <Input
                type="password"
                placeholder="Enter your GitHub token"
                value={accessToken}
                onChange={(e) => setAccessToken(e.target.value)}
              />
              <Text fontSize="sm" color="gray.500" mt={1}>
                The token needs 'repo' scope permissions. Your token is never
                stored on our servers.
              </Text>
            </FormControl>

            <Button
              colorScheme="teal"
              onClick={fetchRepositories}
              isLoading={isLoading && progress === 0}
              loadingText="Connecting"
            >
              Connect to GitHub
            </Button>
          </VStack>
        </CardBody>
      </Card>

      <Card mb={6}>
        <CardHeader>
          <Heading size="md">Repository Selection</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            {repositories.length > 0 && (
              <FormControl>
                <FormLabel>Select a Repository</FormLabel>
                <Select
                  placeholder="Choose from your repositories"
                  value={selectedRepo}
                  onChange={(e) => {
                    setSelectedRepo(e.target.value);
                    setGithubUrl("");
                  }}
                >
                  {repositories.map((repo) => (
                    <option
                      key={`${repo.owner}/${repo.name}`}
                      value={`${repo.owner}/${repo.name}`}
                    >
                      {repo.owner}/{repo.name}
                    </option>
                  ))}
                </Select>
              </FormControl>
            )}

            <Text fontWeight="medium">OR</Text>

            <FormControl isRequired={!selectedRepo}>
              <FormLabel>GitHub Repository URL</FormLabel>
              <Input
                placeholder="https://github.com/username/repository"
                value={githubUrl}
                onChange={(e) => {
                  setGithubUrl(e.target.value);
                  setSelectedRepo("");
                }}
                isDisabled={!!selectedRepo}
              />
            </FormControl>
          </VStack>
        </CardBody>
      </Card>

      <Card mb={6}>
        <CardHeader>
          <Heading size="md">Report Options</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <FormControl>
              <FormLabel>Company Name (Optional)</FormLabel>
              <Input
                placeholder="Your startup name"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
              />
            </FormControl>

            <FormControl>
              <FormLabel>Report Format</FormLabel>
              <Select
                value={reportFormat}
                onChange={(e) => setReportFormat(e.target.value)}
              >
                <option value="html">HTML</option>
                <option value="pdf">PDF</option>
                <option value="markdown">Markdown</option>
              </Select>
            </FormControl>

            <HStack spacing={8}>
              <Checkbox
                isChecked={includeBenchmarks}
                onChange={(e) => setIncludeBenchmarks(e.target.checked)}
              >
                Include industry benchmarks
              </Checkbox>

              <Checkbox
                isChecked={includeSuggestions}
                onChange={(e) => setIncludeSuggestions(e.target.checked)}
              >
                Include suggestions
              </Checkbox>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      {error && (
        <Alert status="error" mb={6} borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Box>
        </Alert>
      )}

      {progress > 0 && (
        <Box mb={6}>
          <Text mb={2}>Analysis in progress: {Math.round(progress)}%</Text>
          <Progress
            value={progress}
            colorScheme="teal"
            hasStripe
            size="lg"
            borderRadius="md"
          />
        </Box>
      )}

      <Button
        colorScheme="blue"
        size="lg"
        width="full"
        onClick={startAnalysis}
        isLoading={isLoading && progress > 0}
        loadingText="Analyzing"
        isDisabled={isLoading || (!githubUrl && !selectedRepo) || !accessToken}
      >
        Start Analysis
      </Button>
    </Box>
  );
};

export default RepositoryAnalysis;
