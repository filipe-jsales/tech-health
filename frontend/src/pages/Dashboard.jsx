import React, { useState, useEffect } from "react";
import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  Button,
  SimpleGrid,
  Card,
  CardBody,
  CardFooter,
  HStack,
  VStack,
  Icon,
  Flex,
  Badge,
  Link,
  useColorModeValue,
  Divider,
  CardHeader,
} from "@chakra-ui/react";
import {
  FiGithub,
  FiFileText,
  FiTrendingUp,
  FiBarChart2,
  FiCode,
  FiArrowRight,
} from "react-icons/fi";
import { Link as RouterLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import axios from "axios";

const Dashboard = () => {
  const { user, getToken } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [reports, setReports] = useState([]);
  const [repositories, setRepositories] = useState([]);
  const [stats, setStats] = useState({
    totalReports: 0,
    totalRepositories: 0,
    averageScore: 0,
    techDebtHours: 0,
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const reportsResponse = await axios.get("http://localhost:8000/api/report/list");
      const reportsData = reportsResponse.data;
      setReports(reportsData.slice(0, 5));

      if (user) {
        const token = getToken();
        const reposResponse = await axios.get("http://localhost:8000/api/github/repositories", {
          params: { access_token: token },
        });
        setRepositories(reposResponse.data.slice(0, 5));

        const totalReports = reportsData.length;
        const totalRepositories = reposResponse.data.length;

        //TODO: In a real app, we would calculate these from actual data
        const averageScore =
          reportsData.length > 0
            ? Math.floor(Math.random() * 30) + 60 //random score between 60-90 for demo
            : 0;

        const techDebtHours =
          reportsData.length > 0
            ? Math.floor(Math.random() * 200) + 50 //random hours between 50-250 for demo
            : 0;

        setStats({
          totalReports,
          totalRepositories,
          averageScore,
          techDebtHours,
        });
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const cardBg = useColorModeValue("white", "gray.700");
  const borderColor = useColorModeValue("gray.200", "gray.600");

  return (
    <Box>
      <Heading mb={6}>Tech Health Dashboard</Heading>

      {user ? (
        <>
          <Text fontSize="lg" mb={8}>
            Welcome back, <strong>{user.username}</strong>! Monitor your
            repositories' technical health and generate investor-ready reports.
          </Text>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
            <StatCard
              title="Total Reports"
              value={stats.totalReports}
              icon={FiFileText}
              colorScheme="blue"
            />
            <StatCard
              title="Repositories"
              value={stats.totalRepositories}
              icon={FiGithub}
              colorScheme="teal"
            />
            <StatCard
              title="Average Score"
              value={`${stats.averageScore}/100`}
              icon={FiBarChart2}
              colorScheme="green"
            />
            <StatCard
              title="Tech Debt (Est.)"
              value={`${stats.techDebtHours} hrs`}
              icon={FiCode}
              colorScheme="orange"
            />
          </SimpleGrid>

          <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6}>
            <GridItem>
              <Card
                bg={cardBg}
                borderWidth="1px"
                borderColor={borderColor}
                borderRadius="lg"
                mb={6}
              >
                <CardHeader>
                  <Heading size="md">Recent Reports</Heading>
                </CardHeader>
                <CardBody>
                  {reports.length === 0 ? (
                    <Box textAlign="center" py={6}>
                      <Icon
                        as={FiFileText}
                        boxSize={12}
                        color="gray.300"
                        mb={4}
                      />
                      <Text color="gray.500" mb={4}>
                        No reports generated yet
                      </Text>
                      <Button
                        as={RouterLink}
                        to="/analyze"
                        colorScheme="blue"
                        leftIcon={<Icon as={FiGithub} />}
                      >
                        Analyze a Repository
                      </Button>
                    </Box>
                  ) : (
                    <VStack align="stretch" spacing={4}>
                      {reports.map((report, index) => (
                        <HStack
                          key={report.id}
                          p={3}
                          borderRadius="md"
                          borderWidth="1px"
                          borderColor={borderColor}
                        >
                          <Icon as={FiFileText} boxSize={6} color="blue.500" />
                          <VStack align="start" flex={1} spacing={0}>
                            <Text fontWeight="bold">{report.repository}</Text>
                          </VStack>
                          <Badge colorScheme="blue">
                            {report.format.toUpperCase()}
                          </Badge>
                          <Button
                            as={Link}
                            href={report.url}
                            size="sm"
                            colorScheme="blue"
                            variant="outline"
                            rightIcon={<FiArrowRight />}
                            target="_blank"
                          >
                            View
                          </Button>
                        </HStack>
                      ))}
                    </VStack>
                  )}
                </CardBody>
                {reports.length > 0 && (
                  <CardFooter>
                    <Button
                      as={RouterLink}
                      to="/reports"
                      rightIcon={<FiArrowRight />}
                      variant="ghost"
                      size="sm"
                      w="full"
                    >
                      View All Reports
                    </Button>
                  </CardFooter>
                )}
              </Card>
            </GridItem>

            <GridItem>
              <Card
                bg={cardBg}
                borderWidth="1px"
                borderColor={borderColor}
                borderRadius="lg"
              >
                <CardHeader>
                  <Heading size="md">Your Repositories</Heading>
                </CardHeader>
                <CardBody>
                  {repositories.length === 0 ? (
                    <Box textAlign="center" py={6}>
                      <Icon
                        as={FiGithub}
                        boxSize={10}
                        color="gray.300"
                        mb={4}
                      />
                      <Text color="gray.500">No repositories found</Text>
                    </Box>
                  ) : (
                    <VStack align="stretch" spacing={3}>
                      {repositories.map((repo) => (
                        <HStack
                          key={repo.name}
                          p={3}
                          borderRadius="md"
                          borderWidth="1px"
                          borderColor={borderColor}
                        >
                          <Icon as={FiGithub} color="gray.600" />
                          <VStack align="start" flex={1} spacing={0}>
                            <Text fontWeight="medium">{repo.name}</Text>
                            <Text fontSize="xs" color="gray.500">
                              {repo.owner}
                            </Text>
                          </VStack>
                          <Button
                            size="sm"
                            colorScheme="blue"
                            onClick={() => {
                              window.location.href = `/analyze?repo=${repo.owner}/${repo.name}`;
                            }}
                          >
                            Analyze
                          </Button>
                        </HStack>
                      ))}
                    </VStack>
                  )}
                </CardBody>
              </Card>
            </GridItem>
          </Grid>

          <Card
            bg={cardBg}
            borderWidth="1px"
            borderColor={borderColor}
            borderRadius="lg"
            mt={8}
          >
            <CardHeader>
              <Heading size="md">How Tech Health Works</Heading>
            </CardHeader>
            <CardBody>
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10}>
                <Feature
                  title="1. Connect Repository"
                  icon={FiGithub}
                  description="Connect your GitHub repository using a personal access token with read-only permissions."
                />
                <Feature
                  title="2. Analyze Code"
                  icon={FiBarChart2}
                  description="Our algorithm analyzes code quality, development patterns, and technical debt."
                />
                <Feature
                  title="3. Generate Report"
                  icon={FiFileText}
                  description="Receive an investor-ready technical health report with benchmarks and recommendations."
                />
              </SimpleGrid>
            </CardBody>
          </Card>
        </>
      ) : (
        <Card
          bg={cardBg}
          borderWidth="1px"
          borderColor={borderColor}
          borderRadius="lg"
          p={8}
          textAlign="center"
        >
          <VStack spacing={6}>
            <Icon as={FiGithub} boxSize={16} color="blue.500" />
            <Heading size="lg">Connect Your GitHub Account</Heading>
            <Text fontSize="lg" maxW="600px" mx="auto">
              Tech Health analyzes your codebase to generate investor-ready
              technical health reports. Connect your GitHub account to get
              started.
            </Text>
            <Button
              size="lg"
              colorScheme="blue"
              as={RouterLink}
              to="/login"
              leftIcon={<FiGithub />}
              mt={4}
            >
              Connect GitHub
            </Button>
          </VStack>

          <Divider my={10} />

          <Heading size="md" mb={8}>
            Key Features
          </Heading>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10}>
            <Feature
              title="Code Quality Analysis"
              icon={FiCode}
              description="Analyze code complexity, maintainability, and test coverage with industry benchmarks."
            />
            <Feature
              title="Development Insights"
              icon={FiTrendingUp}
              description="Track development velocity, commit patterns, and team contributions."
            />
            <Feature
              title="Investor-Ready Reports"
              icon={FiFileText}
              description="Generate professional reports that build investor confidence in your technical foundation."
            />
          </SimpleGrid>
        </Card>
      )}
    </Box>
  );
};

const StatCard = ({ title, value, icon, colorScheme }) => {
  const bgGradient = `linear(to-br, ${colorScheme}.400, ${colorScheme}.600)`;

  return (
    <Box
      p={5}
      borderRadius="lg"
      bgGradient={bgGradient}
      color="white"
      boxShadow="md"
    >
      <Flex justifyContent="space-between" alignItems="center">
        <Box>
          <Text fontSize="sm" fontWeight="medium" mb={1}>
            {title}
          </Text>
          <Text fontSize="2xl" fontWeight="bold">
            {value}
          </Text>
        </Box>
        <Icon as={icon} boxSize={10} opacity={0.8} />
      </Flex>
    </Box>
  );
};

const Feature = ({ title, description, icon }) => {
  return (
    <VStack spacing={4} align="start">
      <Flex
        w={12}
        h={12}
        align="center"
        justify="center"
        borderRadius="full"
        bg="blue.50"
        color="blue.600"
      >
        <Icon as={icon} boxSize={6} />
      </Flex>
      <Text fontWeight="bold" fontSize="lg">
        {title}
      </Text>
      <Text color="gray.500">{description}</Text>
    </VStack>
  );
};

export default Dashboard;
