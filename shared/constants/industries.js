/**
 * Industry options for resume generation
 */
export const INDUSTRIES = [
  {
    id: 'cybersecurity',
    name: 'Cybersecurity',
    description: 'Focus on security skills, certifications, and experience with security tools and frameworks.',
    skills: [
      'Penetration Testing',
      'Vulnerability Assessment',
      'Security Architecture',
      'Incident Response',
      'Threat Intelligence',
      'Network Security',
      'Cloud Security',
      'Security Compliance',
      'SIEM Tools',
      'Security Auditing'
    ],
    certifications: [
      'CISSP',
      'CEH',
      'CompTIA Security+',
      'OSCP',
      'CISM'
    ]
  },
  {
    id: 'legal',
    name: 'Legal',
    description: 'Emphasize case management, research abilities, and specific legal domain expertise.',
    skills: [
      'Legal Research',
      'Case Management',
      'Contract Review',
      'Legal Writing',
      'Client Advocacy',
      'Negotiations',
      'Regulatory Compliance',
      'Litigation Support',
      'Legal Document Preparation',
      'Courtroom Procedures'
    ],
    certifications: [
      'JD (Juris Doctor)',
      'LLM',
      'Bar Association Membership',
      'Certified Paralegal',
      'Legal Project Management'
    ]
  },
  {
    id: 'healthcare',
    name: 'Healthcare',
    description: 'Highlight patient care, compliance with regulations, and relevant medical certifications.',
    skills: [
      'Patient Care',
      'Electronic Health Records (EHR)',
      'HIPAA Compliance',
      'Medical Terminology',
      'Clinical Documentation',
      'Care Coordination',
      'Medical Billing',
      'Healthcare Management',
      'Patient Advocacy',
      'Medical Equipment Operation'
    ],
    certifications: [
      'RN License',
      'CNA Certification',
      'ACLS Certification',
      'BLS Certification',
      'Medical Assistant Certification'
    ]
  },
  {
    id: 'finance',
    name: 'Finance',
    description: 'Emphasize analytical skills, financial certifications, and quantifiable achievements.',
    skills: [
      'Financial Analysis',
      'Investment Management',
      'Risk Assessment',
      'Financial Modeling',
      'Portfolio Management',
      'Financial Reporting',
      'Budgeting',
      'Forecasting',
      'Regulatory Compliance',
      'Mergers & Acquisitions'
    ],
    certifications: [
      'CFA (Chartered Financial Analyst)',
      'CPA (Certified Public Accountant)',
      'FRM (Financial Risk Manager)',
      'CFP (Certified Financial Planner)',
      'Series 7 & 63 Licenses'
    ]
  },
  {
    id: 'tech',
    name: 'Technology',
    description: 'Focus on technical skills, programming languages, and specific frameworks.',
    skills: [
      'Software Development',
      'Full Stack Engineering',
      'Cloud Architecture',
      'DevOps',
      'Agile Methodologies',
      'UI/UX Design',
      'Database Management',
      'API Development',
      'System Administration',
      'Data Science'
    ],
    certifications: [
      'AWS Certified Solutions Architect',
      'Microsoft Certified: Azure Developer',
      'Google Cloud Professional Developer',
      'Certified Scrum Master',
      'Certified Kubernetes Administrator'
    ]
  },
  {
    id: 'general',
    name: 'General',
    description: 'Balanced approach for various professional fields.',
    skills: [
      'Project Management',
      'Team Leadership',
      'Strategic Planning',
      'Communication',
      'Problem Solving',
      'Analytical Thinking',
      'Customer Service',
      'Microsoft Office',
      'Collaboration',
      'Time Management'
    ],
    certifications: [
      'PMP (Project Management Professional)',
      'MBA',
      'Six Sigma Certification',
      'Human Resources Certification',
      'Leadership Training'
    ]
  }
];

/**
 * Get industry data by ID
 * @param {string} id - Industry ID
 * @returns {Object|null} - Industry data or null if not found
 */
export function getIndustryById(id) {
  return INDUSTRIES.find(industry => industry.id === id) || null;
}

/**
 * Get suggestions for skills based on industry
 * @param {string} industryId - Industry ID
 * @param {number} count - Number of suggestions to return
 * @returns {string[]} - Array of skill suggestions
 */
export function getSkillSuggestions(industryId, count = 10) {
  const industry = getIndustryById(industryId);
  
  if (!industry) {
    return getIndustryById('general').skills.slice(0, count);
  }
  
  return industry.skills.slice(0, count);
}

/**
 * Get certification suggestions based on industry
 * @param {string} industryId - Industry ID
 * @returns {string[]} - Array of certification suggestions
 */
export function getCertificationSuggestions(industryId) {
  const industry = getIndustryById(industryId);
  
  if (!industry) {
    return getIndustryById('general').certifications;
  }
  
  return industry.certifications;
}