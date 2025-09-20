export const defaultForm = {
  // Personal Information
  fullName: "John Doe",
  email: "john.doe@example.com",
  phone: "123-456-7890",
  linkedin: "https://linkedin.com/in/johndoe",
  location: "London, UK",
  
  // Resume Details
  title: "Cybersecurity Professional Resume",
  targetJobTitle: "Senior Security Analyst",
  targetJobRole: "Security Analyst",
  targetCompany: "TechCorp Industries",
  industry: "cybersecurity",
  
  // Professional Summary
  summary: "Experienced cybersecurity professional with expertise in threat analysis and network security.",
  
  // Skills
  skills: ["Network Security", "Linux Administration", "Python", "SIEM Tools", "Incident Response"],
  
  // Work Experience
  workExperience: [
    {
      title: "Security Analyst",
      company: "CyberSafe Ltd",
      location: "Remote",
      startDate: "2022-01",
      endDate: "2023-12",
      description: "Monitored security systems and investigated potential threats. Implemented security protocols and conducted vulnerability assessments.",
      highlights: [
        "Reduced security incidents by 45% through proactive monitoring",
        "Led incident response team for critical security breaches",
        "Implemented automated threat detection systems"
      ]
    },
    {
      title: "Junior Security Analyst",
      company: "SecureNet Solutions",
      location: "London, UK",
      startDate: "2021-07",
      endDate: "2021-12",
      description: "Assisted senior analysts in monitoring network traffic and identifying security vulnerabilities.",
      highlights: [
        "Analyzed over 1000 security alerts weekly",
        "Contributed to security policy documentation"
      ]
    }
  ],
  
  // Education
  education: [
    {
      degree: "BSc Cybersecurity",
      school: "Tech University",
      location: "London, UK",
      graduationDate: "2021-06",
      description: "Graduated with First Class Honours. Specialized in network security and digital forensics.",
      gpa: "3.8"
    }
  ],
  
  // Section toggles
  includeProjects: true,
  includeCertifications: true,
  includeLanguages: true,
  
  // Projects (new structure)
  projects: [
    {
      title: "Network Security Monitoring Dashboard",
      description: "Developed a real-time dashboard for monitoring network security events using Python and Grafana. Integrated with multiple SIEM tools to provide centralized threat visibility.",
      technologies: ["Python", "Grafana", "Elasticsearch", "Docker", "Linux"],
      url: "https://github.com/johndoe/security-dashboard",
      startDate: "2023-03",
      endDate: "2023-08",
      highlights: [
        "Reduced threat detection time by 60%",
        "Processed over 10M security events daily",
        "Implemented automated alerting system"
      ]
    },
    {
      title: "Vulnerability Assessment Tool",
      description: "Created an automated vulnerability scanning tool that integrates with existing security infrastructure. Built using Python with custom plugins for different system types.",
      technologies: ["Python", "Nmap", "SQL", "REST APIs"],
      url: "",
      startDate: "2022-09",
      endDate: "2023-01",
      highlights: [
        "Automated 80% of manual vulnerability checks",
        "Discovered 150+ critical vulnerabilities across infrastructure"
      ]
    }
  ],
  
  // Certifications
  certifications: [
    { name: "CompTIA Security+", issuer: 'CompTIA', date: '2023-06', expiryDate: '2026-06', credentialId: "COMP001234567" },
    { name: "Certified Ethical Hacker (CEH)", issuer: 'EC-Council', date: '2022-11', expiryDate: '2025-11', credentialId: "ECC-CEH-2022-001" },
    { name: "AWS Certified Security - Specialty", issuer: 'Amazon Web Services', date: '2023-03', expiryDate: '2026-03', credentialId: "AWS-CSS-2023-789" },
  ],
  

  // Languages (new structure)
  languages: [
    {
      language: "English",
      proficiency: "Native"
    },
    {
      language: "Spanish",
      proficiency: "Intermediate"
    },
    {
      language: "French",
      proficiency: "Beginner"
    }
  ],
  
  // AI Settings
  useAI: true,
  aiTone: "professional",
  aiLength: "standard"
};