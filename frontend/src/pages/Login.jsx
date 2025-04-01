import React, { useState } from "react";
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Stack,
  Text,
  Link,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  VStack,
  HStack,
} from "@chakra-ui/react";
import { FiGithub, FiCheckCircle } from "react-icons/fi";
import { useAuth } from "../context/AuthContext";

const Login = () => {
  const [token, setToken] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!token.trim()) {
      setError("GitHub token is required");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const result = await login(token);
      if (!result.success) {
        setError(result.message);
      }
    } catch (error) {
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Flex
      minH={"100vh"}
      align={"center"}
      justify={"center"}
      bg={useColorModeValue("gray.50", "gray.800")}
    >
      <Stack spacing={8} mx={"auto"} maxW={"lg"} py={12} px={6} width="full">
        <Stack align={"center"}>
          <Heading fontSize={"4xl"} textAlign="center">
            Tech Health
          </Heading>
          <Text fontSize={"lg"} color={"gray.600"} textAlign="center">
            Analyze your codebase and generate investor-ready technical health
            reports
          </Text>
        </Stack>
        <Box
          rounded={"lg"}
          bg={useColorModeValue("white", "gray.700")}
          boxShadow={"lg"}
          p={8}
        >
          {error && (
            <Alert status="error" mb={4} borderRadius="md">
              <AlertIcon />
              <AlertTitle mr={2}>Authentication Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <VStack spacing={4} as="form" onSubmit={handleLogin}>
            <FormControl id="token" isRequired>
              <FormLabel>GitHub Personal Access Token</FormLabel>
              <Input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Enter your GitHub token"
              />
              <Text mt={2} fontSize="sm" color="gray.500">
                Token needs 'repo' scope permissions to access your
                repositories.
              </Text>
            </FormControl>

            <Button
              bg={"blue.400"}
              color={"white"}
              _hover={{
                bg: "blue.500",
              }}
              type="submit"
              width="full"
              isLoading={isLoading}
              leftIcon={<FiGithub />}
            >
              Connect with GitHub
            </Button>
          </VStack>

          <Divider my={6} />

          <VStack spacing={4}>
            <Heading size="sm">How to create a GitHub token:</Heading>
            <HStack alignItems="flex-start" spacing={4}>
              <Box
                bg="blue.50"
                color="blue.600"
                borderRadius="full"
                width="24px"
                height="24px"
                display="flex"
                alignItems="center"
                justifyContent="center"
                fontWeight="bold"
              >
                1
              </Box>
              <Box flex={1}>
                <Text fontWeight="medium">Go to GitHub Settings</Text>
                <Text fontSize="sm">
                  Visit{" "}
                  <Link
                    color="blue.500"
                    href="https://github.com/settings/tokens"
                    isExternal
                  >
                    https://github.com/settings/tokens
                  </Link>
                </Text>
              </Box>
            </HStack>

            <HStack alignItems="flex-start" spacing={4}>
              <Box
                bg="blue.50"
                color="blue.600"
                borderRadius="full"
                width="24px"
                height="24px"
                display="flex"
                alignItems="center"
                justifyContent="center"
                fontWeight="bold"
              >
                2
              </Box>
              <Box flex={1}>
                <Text fontWeight="medium">Generate a New Token</Text>
                <Text fontSize="sm">
                  Click "Generate new token" and authenticate if required
                </Text>
              </Box>
            </HStack>

            <HStack alignItems="flex-start" spacing={4}>
              <Box
                bg="blue.50"
                color="blue.600"
                borderRadius="full"
                width="24px"
                height="24px"
                display="flex"
                alignItems="center"
                justifyContent="center"
                fontWeight="bold"
              >
                3
              </Box>
              <Box flex={1}>
                <Text fontWeight="medium">Set Token Permissions</Text>
                <Text fontSize="sm">
                  Give it a name and select the "repo" scope to allow read
                  access to your repositories
                </Text>
              </Box>
            </HStack>

            <HStack alignItems="flex-start" spacing={4}>
              <Box
                bg="blue.50"
                color="blue.600"
                borderRadius="full"
                width="24px"
                height="24px"
                display="flex"
                alignItems="center"
                justifyContent="center"
                fontWeight="bold"
              >
                4
              </Box>
              <Box flex={1}>
                <Text fontWeight="medium">Copy & Paste Token</Text>
                <Text fontSize="sm">
                  Copy your new token and paste it above to log in
                </Text>
              </Box>
            </HStack>
          </VStack>

          <Alert status="info" mt={6} borderRadius="md">
            <AlertIcon as={FiCheckCircle} />
            <Box>
              <AlertTitle>Your Code Stays Private</AlertTitle>
              <AlertDescription>
                We only request read access to analyze your code. Your code is
                never stored on our servers.
              </AlertDescription>
            </Box>
          </Alert>
        </Box>
      </Stack>
    </Flex>
  );
};

export default Login;
