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
  Switch,
  Select,
  HStack,
  Divider,
  Card,
  CardHeader,
  CardBody,
  useColorModeValue,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  useDisclosure,
} from "@chakra-ui/react";
import { useAuth } from "../context/AuthContext";

const Settings = () => {
  const { user, logout, getToken } = useAuth();
  const [githubToken, setGithubToken] = useState("");
  const [defaultReportFormat, setDefaultReportFormat] = useState("html");
  const [emailNotifications, setEmailNotifications] = useState(false);
  const [email, setEmail] = useState("");
  const [autoAnalysis, setAutoAnalysis] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const cancelRef = React.useRef();

  const cardBg = useColorModeValue("white", "gray.700");
  const borderColor = useColorModeValue("gray.200", "gray.600");

  const handleSaveSettings = () => {
    setIsUpdating(true);

    //TODO: In a real app, this would make an API call to save settings
    setTimeout(() => {
      setIsUpdating(false);

      toast({
        title: "Settings saved",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    }, 1000);
  };

  const handleUpdateToken = () => {
    setIsUpdating(true);

    //TODO: In a real app, this would validate the token and update it
    setTimeout(() => {
      setIsUpdating(false);

      toast({
        title: "GitHub token updated",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    }, 1000);
  };

  const handleLogout = () => {
    onClose();
    logout();
  };

  return (
    <Box maxW="800px" mx="auto">
      <Heading mb={6}>Settings</Heading>

      <Card
        bg={cardBg}
        borderWidth="1px"
        borderColor={borderColor}
        borderRadius="lg"
        mb={6}
      >
        <CardHeader>
          <Heading size="md">GitHub Integration</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={6} align="stretch">
            <Box>
              <Text fontWeight="medium" mb={2}>
                Current GitHub Account
              </Text>
              <HStack>
                <Text>{user?.username || "Not connected"}</Text>
                <Button
                  size="sm"
                  colorScheme="red"
                  variant="outline"
                  onClick={onOpen}
                >
                  Disconnect
                </Button>
              </HStack>
            </Box>

            <Divider />

            <FormControl>
              <FormLabel>Update GitHub Token</FormLabel>
              <HStack>
                <Input
                  type="password"
                  placeholder="Enter new GitHub token"
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                />
                <Button
                  colorScheme="blue"
                  onClick={handleUpdateToken}
                  isLoading={isUpdating}
                  isDisabled={!githubToken}
                >
                  Update
                </Button>
              </HStack>
              <Text fontSize="sm" color="gray.500" mt={1}>
                Update your GitHub token if it has expired or you need different
                permissions
              </Text>
            </FormControl>
          </VStack>
        </CardBody>
      </Card>

      <Card
        bg={cardBg}
        borderWidth="1px"
        borderColor={borderColor}
        borderRadius="lg"
        mb={6}
      >
        <CardHeader>
          <Heading size="md">Report Preferences</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={6} align="stretch">
            <FormControl>
              <FormLabel>Default Report Format</FormLabel>
              <Select
                value={defaultReportFormat}
                onChange={(e) => setDefaultReportFormat(e.target.value)}
              >
                <option value="html">HTML</option>
                <option value="pdf">PDF</option>
                <option value="markdown">Markdown</option>
              </Select>
            </FormControl>

            <FormControl display="flex" alignItems="center">
              <FormLabel mb="0">Include Industry Benchmarks</FormLabel>
              <Switch defaultChecked colorScheme="blue" />
            </FormControl>

            <FormControl display="flex" alignItems="center">
              <FormLabel mb="0">Include Optimization Suggestions</FormLabel>
              <Switch defaultChecked colorScheme="blue" />
            </FormControl>
          </VStack>
        </CardBody>
      </Card>

      <Card
        bg={cardBg}
        borderWidth="1px"
        borderColor={borderColor}
        borderRadius="lg"
        mb={6}
      >
        <CardHeader>
          <Heading size="md">Notifications</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={6} align="stretch">
            <FormControl display="flex" alignItems="center">
              <FormLabel mb="0">Email Notifications</FormLabel>
              <Switch
                colorScheme="blue"
                isChecked={emailNotifications}
                onChange={(e) => setEmailNotifications(e.target.checked)}
              />
            </FormControl>

            {emailNotifications && (
              <FormControl>
                <FormLabel>Email Address</FormLabel>
                <Input
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </FormControl>
            )}

            <FormControl display="flex" alignItems="center">
              <FormLabel mb="0">Automatic Weekly Analysis</FormLabel>
              <Switch
                colorScheme="blue"
                isChecked={autoAnalysis}
                onChange={(e) => setAutoAnalysis(e.target.checked)}
              />
            </FormControl>

            {autoAnalysis && (
              <Text color="gray.500" fontSize="sm">
                Your repositories will be automatically analyzed every week to
                track technical health over time.
              </Text>
            )}
          </VStack>
        </CardBody>
      </Card>

      <Button
        colorScheme="blue"
        size="lg"
        width="full"
        onClick={handleSaveSettings}
        isLoading={isUpdating}
      >
        Save Settings
      </Button>

      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Disconnect GitHub Account
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure? This will log you out and you'll need to reconnect
              your GitHub account to use Tech Health.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={handleLogout} ml={3}>
                Disconnect
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  );
};

export default Settings;
