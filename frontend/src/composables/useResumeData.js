// composables/useResumeData.js
import { ref, computed, watch, nextTick } from 'vue'
import { useToast } from '@/composables/useToast'
import { defaultForm } from '@/utils/defaultForm'

/**
 * Composable for managing resume data with autosave functionality
 */
export function useResumeData() {
  const resumeData = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Autosave state
  const isAutoSaving = ref(false)
  const lastSaved = ref(null)
  const isDirty = ref(false)
  const autoSaveError = ref(null)
  const saveTimeout = ref(null)
  const hasUnsavedChanges = ref(false)
  
  // Autosave configuration
  const autoSaveConfig = ref({
    enabled: true,
    interval: 3000, // 3 seconds
    storageKey: 'resumeFormData',
    maxRetries: 3,
    retryDelay: 1000,
    showNotifications: false // Set to true if you want save notifications
  })

  const { success, error: showError, info } = useToast()

  // Check if we're in browser environment
  const isBrowser = typeof window !== 'undefined'

  // Standard form structure that the UI expects
  const createEmptyFormStructure = () => {
    const structure = {
      // Meta information
      id: null,
      title: '',
      
      // Target information
      targetJobTitle: '',
      targetJobRole: '',
      targetCompany: '',
      industry: '',
      
      // Personal information
      fullName: '',
      email: '',
      phone: '',
      linkedin: '',
      location: '',
      
      // Content
      summary: '',
      skills: [],
      
      // Experience and education
      workExperience: [{
        title: '',
        company: '',
        location: '',
        startDate: '',
        endDate: '',
        current: false,
        description: '',
        highlights: ['']
      }],
      
      education: [{
        degree: '',
        school: '',
        location: '',
        graduationDate: '',
        description: '',
        gpa: ''
      }],
      
      // Optional sections
      projects: [],
      certifications: [{
        name: '',
        issuer: '',
        date: '',
        expiryDate: '',
        credentialId: ''
      }],
      languages: [],
      
      // Section toggles
      includeProjects: false,
      includeCertifications: false,
      includeLanguages: false,
      
      // AI settings
      useAI: true,
      aiTone: 'professional',
      aiLength: 'standard',
      
      // Template
      templateId: 1,
      
      // Keywords
      focusKeywords: []
    }
    
    console.log('createEmptyFormStructure called, returning:', {
      hasTitle: typeof structure.title === 'string',
      titleValue: structure.title,
      hasTargetJobTitle: typeof structure.targetJobTitle === 'string',
      hasRequiredFields: structure.fullName !== undefined && structure.email !== undefined
    })
    
    return structure
  }

  /**
   * Normalize API response data to consistent form structure
   */
  const normalizeApiResponse = (apiData) => {
    console.log('=== NORMALIZE API RESPONSE DEBUG ===')
    console.log('Input apiData:', JSON.stringify(apiData, null, 2))
    
    if (!apiData) {
      console.log('No apiData provided, returning empty structure')
      return createEmptyFormStructure()
    }

    const normalized = createEmptyFormStructure()

    try {
      // Basic resume information
      normalized.id = apiData.id || null
      normalized.title = apiData.title || ''
      
      console.log('Basic info normalized:')
      console.log('- id:', normalized.id)
      console.log('- title:', normalized.title)
      
      // IMPORTANT: Set include flags from original data FIRST
      // This prevents them from being overridden by array length logic later
      normalized.includeProjects = apiData.includeProjects ?? normalized.includeProjects
      normalized.includeCertifications = apiData.includeCertifications ?? normalized.includeCertifications  
      normalized.includeLanguages = apiData.includeLanguages ?? normalized.includeLanguages
      
      console.log('Include flags from original data:')
      console.log('- includeProjects:', apiData.includeProjects, '->', normalized.includeProjects)
      console.log('- includeCertifications:', apiData.includeCertifications, '->', normalized.includeCertifications)
      console.log('- includeLanguages:', apiData.includeLanguages, '->', normalized.includeLanguages)
      
      // Target information - handle both snake_case and camelCase
      normalized.targetJobTitle = apiData.target_job_title || apiData.targetJobTitle || ''
      normalized.targetJobRole = apiData.target_job_role || apiData.targetJobRole || ''
      normalized.targetCompany = apiData.target_company || apiData.targetCompany || ''
      normalized.industry = apiData.industry || ''
      
      console.log('Target info normalized:')
      console.log('- targetJobTitle:', normalized.targetJobTitle)
      console.log('- targetJobRole:', normalized.targetJobRole)
      console.log('- targetCompany:', normalized.targetCompany)
      console.log('- industry:', normalized.industry)
      
      // AI settings
      normalized.aiTone = apiData.ai_tone || apiData.aiTone || 'professional'
      normalized.aiLength = apiData.ai_length || apiData.aiLength || 'standard'
      normalized.useAI = apiData.use_ai ?? apiData.useAI ?? true
      
      // Template
      normalized.templateId = apiData.template_id || apiData.templateId || 1
      
      // Keywords
      normalized.focusKeywords = apiData.focus_keywords || apiData.focusKeywords || []
      
      // Handle profile data (could be nested or flat)
      const profileData = apiData.profile_data || apiData.profile || apiData
      
      console.log('Profile data structure:', profileData ? Object.keys(profileData) : 'null')
      
      if (profileData) {
        // Personal information
        normalized.fullName = profileData.full_name || profileData.fullName || ''
        normalized.email = profileData.email || ''
        normalized.phone = profileData.phone || ''
        normalized.linkedin = profileData.linkedin || ''
        normalized.location = profileData.location || ''
        normalized.summary = profileData.summary || ''
        
        console.log('Personal info normalized:')
        console.log('- fullName:', normalized.fullName)
        console.log('- email:', normalized.email)
        console.log('- phone:', normalized.phone)
        console.log('- linkedin:', normalized.linkedin)
        console.log('- location:', normalized.location)
        console.log('- summary length:', normalized.summary.length)
        
        // Skills - ensure it's always an array
        normalized.skills = Array.isArray(profileData.skills) ? profileData.skills : []
        console.log('- skills:', normalized.skills.length, 'items')
        
        // Work Experience
        console.log('Raw work experience:', profileData.work_experience || profileData.workExperience)
        normalized.workExperience = normalizeWorkExperience(
          profileData.work_experience || profileData.workExperience
        )
        console.log('Normalized work experience:', normalized.workExperience.length, 'items')
        
        // Education
        console.log('Raw education:', profileData.education)
        normalized.education = normalizeEducation(profileData.education)
        console.log('Normalized education:', normalized.education.length, 'items')
        
        // Projects
        console.log('Raw projects:', profileData.projects)
        normalized.projects = normalizeProjects(profileData.projects)
        // Only auto-set include flags if they weren't explicitly provided in original data
        const hasExplicitIncludeProjects = apiData.includeProjects !== undefined || apiData.include_projects !== undefined
        if (!hasExplicitIncludeProjects && normalized.projects.length > 0) {
          normalized.includeProjects = true
        }
        console.log('Normalized projects:', normalized.projects.length, 'items, include:', normalized.includeProjects, 'explicit:', hasExplicitIncludeProjects)
        
        // Certifications
        console.log('Raw certifications:', profileData.certifications)
        normalized.certifications = normalizeCertifications(profileData.certifications)
        const hasExplicitIncludeCertifications = apiData.includeCertifications !== undefined || apiData.include_certifications !== undefined
        if (!hasExplicitIncludeCertifications && normalized.certifications.length > 0) {
          normalized.includeCertifications = true
        }
        console.log('Normalized certifications:', normalized.certifications.length, 'items, include:', normalized.includeCertifications, 'explicit:', hasExplicitIncludeCertifications)
        
        // Languages
        console.log('Raw languages:', profileData.languages)
        normalized.languages = normalizeLanguages(profileData.languages)
        const hasExplicitIncludeLanguages = apiData.includeLanguages !== undefined || apiData.include_languages !== undefined
        if (!hasExplicitIncludeLanguages && normalized.languages.length > 0) {
          normalized.includeLanguages = true
        }
        console.log('Normalized languages:', normalized.languages.length, 'items, include:', normalized.includeLanguages, 'explicit:', hasExplicitIncludeLanguages)
      }
      
      // Section toggles - check for explicit API overrides
      const originalIncludeProjects = normalized.includeProjects
      const originalIncludeCertifications = normalized.includeCertifications
      const originalIncludeLanguages = normalized.includeLanguages
      
      normalized.includeProjects = apiData.include_projects ?? normalized.includeProjects
      normalized.includeCertifications = apiData.include_certifications ?? normalized.includeCertifications
      normalized.includeLanguages = apiData.include_languages ?? normalized.includeLanguages
      
      console.log('Section toggles:')
      console.log('- includeProjects:', originalIncludeProjects, '->', normalized.includeProjects, '(API override:', apiData.include_projects, ')')
      console.log('- includeCertifications:', originalIncludeCertifications, '->', normalized.includeCertifications, '(API override:', apiData.include_certifications, ')')
      console.log('- includeLanguages:', originalIncludeLanguages, '->', normalized.includeLanguages, '(API override:', apiData.include_languages, ')')
      
      console.log('FINAL NORMALIZED DATA:')
      console.log('- Projects:', normalized.projects?.length || 0, 'items, include:', normalized.includeProjects)
      console.log('- Certifications:', normalized.certifications?.length || 0, 'items, include:', normalized.includeCertifications)  
      console.log('- Languages:', normalized.languages?.length || 0, 'items, include:', normalized.includeLanguages)
      
      console.log('=== END NORMALIZE DEBUG ===')
      return normalized
    } catch (error) {
      console.error('Error normalizing API response:', error)
      console.log('=== END NORMALIZE DEBUG (ERROR) ===')
      return createEmptyFormStructure()
    }
  }

  /**
   * Normalize work experience data
   */
  const normalizeWorkExperience = (workExp) => {
    if (!Array.isArray(workExp) || workExp.length === 0) {
      return [{
        title: '',
        company: '',
        location: '',
        startDate: '',
        endDate: '',
        current: false,
        description: '',
        highlights: ['']
      }]
    }

    return workExp.map(exp => ({
      title: exp.title || '',
      company: exp.company || '',
      location: exp.location || '',
      startDate: exp.start_date || exp.startDate || '',
      endDate: exp.end_date || exp.endDate || '',
      current: exp.current ?? (!exp.end_date && !exp.endDate),
      description: exp.description || '',
      highlights: Array.isArray(exp.highlights) ? exp.highlights : 
                  exp.highlights ? [exp.highlights] : ['']
    }))
  }

  /**
   * Normalize education data
   */
  const normalizeEducation = (education) => {
    if (!Array.isArray(education) || education.length === 0) {
      return [{
        degree: '',
        school: '',
        location: '',
        graduationDate: '',
        description: '',
        gpa: ''
      }]
    }

    return education.map(edu => ({
      degree: edu.degree || '',
      school: edu.school || '',
      location: edu.location || '',
      graduationDate: edu.graduation_date || edu.graduationDate || '',
      description: edu.description || '',
      gpa: edu.gpa || ''
    }))
  }

  /**
   * Normalize projects data
   */
  const normalizeProjects = (projects) => {
    if (!Array.isArray(projects)) return []

    return projects.map(project => ({
      title: project.title || '',
      description: project.description || '',
      technologies: Array.isArray(project.technologies) ? project.technologies : [],
      url: project.url || '',
      startDate: project.start_date || project.startDate || '',
      endDate: project.end_date || project.endDate || '',
      highlights: Array.isArray(project.highlights) ? project.highlights : ['']
    }))
  }

  /**
   * Normalize certifications data
   */
  const normalizeCertifications = (certifications) => {
    if (!Array.isArray(certifications)) return []

    return certifications.map(cert => {
      if (typeof cert === 'string') {
        return {
          name: cert,
          issuer: '',
          date: '',
          expiryDate: '',
          credentialId: ''
        }
      }
      
      return {
        name: cert.name || cert.title || '',
        issuer: cert.issuer || cert.organization || '',
        date: cert.date || cert.issued_date || cert.issuedDate || '',
        expiryDate: cert.expiryDate || cert.expiry_date || cert.expirationDate || '',
        credentialId: cert.credentialId || cert.credential_id || cert.verificationUrl || cert.url || ''
      }
    })
  }

  /**
   * Normalize languages data
   */
  const normalizeLanguages = (languages) => {
    if (!Array.isArray(languages)) return []

    return languages.map(lang => {
      if (typeof lang === 'string') {
        return {
          name: lang,
          proficiency: 'conversational'
        }
      }
      
      return {
        name: lang.name || lang.language || '',
        proficiency: lang.proficiency || lang.level || 'conversational'
      }
    })
  }

  /**
   * Convert form data back to API payload format
   */
  const toApiPayload = (formData) => {
    const payload = {
      title: formData.title,
      target_job_title: formData.targetJobTitle,
      target_job_role: formData.targetJobRole,
      target_company: formData.targetCompany,
      industry: formData.industry,
      ai_tone: formData.aiTone,
      ai_length: formData.aiLength,
      use_ai: formData.useAI,
      template_id: formData.templateId,
      focus_keywords: formData.focusKeywords,
      include_projects: formData.includeProjects,
      include_certifications: formData.includeCertifications,
      include_languages: formData.includeLanguages,
      
      profile_data: {
        full_name: formData.fullName,
        email: formData.email?.trim() || null,
        phone: formData.phone?.trim() || null,
        linkedin: formData.linkedin?.trim() || null,
        location: formData.location?.trim() || null,
        summary: formData.summary?.trim() || null,
        skills: formData.skills || [],
        
        work_experience: formData.workExperience?.map(exp => ({
          title: exp.title || '',
          company: exp.company || '',
          location: exp.location || '',
          start_date: exp.startDate || '',
          end_date: exp.endDate || '',
          current: exp.current || !exp.endDate,
          description: exp.description || '',
          highlights: exp.highlights || []
        })) || [],
        
        education: formData.education?.map(edu => ({
          degree: edu.degree || '',
          school: edu.school || '',
          location: edu.location || '',
          graduation_date: edu.graduationDate || '',
          description: edu.description || '',
          gpa: edu.gpa || ''
        })) || [],
        
        projects: formData.projects?.map(project => ({
          title: project.title || '',
          description: project.description || '',
          technologies: project.technologies || [],
          url: project.url || '',
          start_date: project.startDate || '',
          end_date: project.endDate || '',
          highlights: project.highlights || []
        })) || [],
        
        certifications: formData.certifications?.map(cert => {
          if (typeof cert === 'string') return cert
          return {
            name: cert.name || '',
            issuer: cert.issuer || '',
            date: cert.date || '',
            expiry_date: cert.expiryDate || '',
            credential_id: cert.credentialId || ''
          }
        }) || [],
        
        languages: formData.languages?.map(lang => ({
          language: lang.name || lang.language || '',
          proficiency: lang.proficiency || lang.level || 'conversational'
        })) || []
      }
    }

    return cleanObject(payload)
  }

  /**
   * Clean object by removing null/undefined values
   */
  const cleanObject = (obj) => {
    if (Array.isArray(obj)) {
      return obj.map(cleanObject).filter(item => item !== null && item !== undefined)
    }
    
    if (obj && typeof obj === 'object') {
      const cleaned = {}
      for (const [key, value] of Object.entries(obj)) {
        if (value !== null && value !== undefined) {
          if (typeof value === 'string' && value.trim() === '') {
            continue
          }
          cleaned[key] = cleanObject(value)
        }
      }
      return cleaned
    }
    
    return obj
  }

  /**
   * Save data to localStorage with error handling
   */
  const saveToStorage = async (data, key = null, retryCount = 0) => {
    if (!isBrowser) return { success: false, error: 'Not in browser environment' }

    const storageKey = key || autoSaveConfig.value.storageKey

    try {
      const dataToSave = {
        data,
        timestamp: Date.now(),
        version: '1.0'
      }
      
      localStorage.setItem(storageKey, JSON.stringify(dataToSave))
      
      lastSaved.value = new Date()
      isDirty.value = false
      hasUnsavedChanges.value = false
      autoSaveError.value = null
      
      if (autoSaveConfig.value.showNotifications) {
        info('Draft saved', { duration: 1000 })
      }
      
      return { success: true }
    } catch (error) {
      console.error('Error saving to localStorage:', error)
      
      // Retry logic
      if (retryCount < autoSaveConfig.value.maxRetries) {
        console.log(`Retrying save... Attempt ${retryCount + 1}`)
        
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve(saveToStorage(data, key, retryCount + 1))
          }, autoSaveConfig.value.retryDelay)
        })
      }
      
      autoSaveError.value = error.message
      showError('Failed to save draft')
      return { success: false, error: error.message }
    }
  }

  /**
   * Load data from localStorage with versioning
   */
  const loadFromStorage = (key = null) => {
    if (!isBrowser) return null

    const storageKey = key || autoSaveConfig.value.storageKey

    try {
      const stored = localStorage.getItem(storageKey)
      if (!stored) return null

      const parsedData = JSON.parse(stored)
      
      // Handle both old format (direct data) and new format (with metadata)
      if (parsedData.data && parsedData.timestamp) {
        // New format with metadata
        lastSaved.value = new Date(parsedData.timestamp)
        return normalizeApiResponse(parsedData.data)
      } else {
        // Old format - direct data
        return normalizeApiResponse(parsedData)
      }
    } catch (error) {
      console.error('Error loading from localStorage:', error)
      return null
    }
  }

  /**
   * Clear storage
   */
  const clearStorage = (keys = ['resumeFormData', 'currentResumeId', 'editMode']) => {
    if (!isBrowser) return

    keys.forEach(key => {
      localStorage.removeItem(key)
    })
    
    lastSaved.value = null
    isDirty.value = false
    hasUnsavedChanges.value = false
  }

  /**
   * Debounced autosave function
   */
  const triggerAutoSave = () => {
    if (!autoSaveConfig.value.enabled || !resumeData.value) return

    // Clear existing timeout
    if (saveTimeout.value) {
      clearTimeout(saveTimeout.value)
    }

    // Mark as dirty
    isDirty.value = true
    hasUnsavedChanges.value = true

    // Set new timeout
    saveTimeout.value = setTimeout(async () => {
      if (resumeData.value && isDirty.value) {
        isAutoSaving.value = true
        await saveToStorage(resumeData.value)
        isAutoSaving.value = false
      }
    }, autoSaveConfig.value.interval)
  }

  /**
   * Force save immediately
   */
  const forceSave = async () => {
    if (!resumeData.value) return { success: false, error: 'No data to save' }

    if (saveTimeout.value) {
      clearTimeout(saveTimeout.value)
    }

    isAutoSaving.value = true
    const result = await saveToStorage(resumeData.value)
    isAutoSaving.value = false

    return result
  }

  /**
   * Enable/disable autosave
   */
  const setAutoSaveEnabled = (enabled) => {
    autoSaveConfig.value.enabled = enabled
    
    if (!enabled && saveTimeout.value) {
      clearTimeout(saveTimeout.value)
      saveTimeout.value = null
    }
  }

  /**
   * Update autosave configuration
   */
  const updateAutoSaveConfig = (newConfig) => {
    autoSaveConfig.value = { ...autoSaveConfig.value, ...newConfig }
  }

  /**
   * Initialize form data with proper structure
   */
  const initializeFormData = (existingData = null) => {
    let formData

    console.log('=== RESUME DATA INITIALIZATION DEBUG ===')
    console.log('Environment Details:')
    console.log('- NODE_ENV:', process.env.NODE_ENV)
    console.log('- isBrowser:', isBrowser)
    console.log('- location.hostname:', isBrowser ? window.location.hostname : 'N/A')
    console.log('- location.href:', isBrowser ? window.location.href : 'N/A')
    console.log('- existingData provided:', !!existingData)
    
    if (existingData) {
      console.log('Raw existingData structure:', JSON.stringify(existingData, null, 2))
    }

    if (existingData) {
      console.log('Using existing data provided')
      formData = normalizeApiResponse(existingData)
    } else {
      const editMode = isBrowser && localStorage.getItem('editMode') === 'true'
      const resumeId = isBrowser && localStorage.getItem('currentResumeId')

      console.log('LocalStorage state:')
      console.log('- editMode:', editMode)
      console.log('- resumeId:', resumeId)
      
      if (isBrowser) {
        console.log('- localStorage keys:', Object.keys(localStorage))
        console.log('- resumeFormData exists:', !!localStorage.getItem('resumeFormData'))
      }

      if (editMode && resumeId) {
        console.log('Loading from storage for edit mode')
        const storedData = loadFromStorage()
        console.log('Stored data loaded:', !!storedData)
        if (storedData) {
          console.log('Stored data structure:', JSON.stringify(storedData, null, 2))
        }
        formData = storedData || createEmptyFormStructure()
      } else {
        const isLocalhost = isBrowser && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
        const hasTestDataParam = isBrowser && new URLSearchParams(window.location.search).has('testdata')
        const isDevelopment = process.env.NODE_ENV === 'development'
        const useTestData = isDevelopment || isLocalhost || hasTestDataParam
        
        console.log('Test data conditions:')
        console.log('- isDevelopment:', isDevelopment)
        console.log('- isLocalhost:', isLocalhost)
        console.log('- hasTestDataParam:', hasTestDataParam)
        console.log('- useTestData:', useTestData)
        
        formData = useTestData ? loadTestData() : createEmptyFormStructure()
      }
    }

    console.log('Form data after initialization:')
    console.log('- Data structure keys:', Object.keys(formData))
    console.log('- includeProjects:', formData.includeProjects)
    console.log('- includeCertifications:', formData.includeCertifications)
    console.log('- includeLanguages:', formData.includeLanguages)
    console.log('- projects length:', formData.projects?.length)
    console.log('- certifications length:', formData.certifications?.length)
    console.log('- languages length:', formData.languages?.length)
    
    console.log('Null/undefined/empty values found:')
    Object.entries(formData).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) {
        console.log(`- ${key}: ${JSON.stringify(value)} (${typeof value})`)
      }
    })
    console.log('=== END INITIALIZATION DEBUG ===')

    // Initialize resume data immediately to prevent template errors
    resumeData.value = formData
    isDirty.value = false
    hasUnsavedChanges.value = false

    // Set up autosave watcher after data is set
    if (isBrowser) {
      setupAutoSaveWatcher()
    }

    return formData
  }

  /**
   * Setup autosave watcher
   */
  const setupAutoSaveWatcher = () => {
    if (!isBrowser) return

    console.log('Setting up autosave watcher...')

    // Watch for changes and trigger autosave
    watch(
      resumeData,
      (newData, oldData) => {
        if (resumeData.value) {
          console.log('=== RESUME DATA CHANGE DETECTED ===')
          console.log('New data keys:', newData ? Object.keys(newData) : 'null')
          console.log('Section toggles changed:')
          console.log('- includeProjects:', oldData?.includeProjects, '->', newData?.includeProjects)
          console.log('- includeCertifications:', oldData?.includeCertifications, '->', newData?.includeCertifications)  
          console.log('- includeLanguages:', oldData?.includeLanguages, '->', newData?.includeLanguages)
          
          // Check for specific null/empty changes
          if (newData) {
            const nullValues = Object.entries(newData).filter(([, value]) => 
              value === null || value === undefined || value === ''
            )
            if (nullValues.length > 0) {
              console.log('Null/empty values in change:', nullValues.map(([k, v]) => `${k}: ${v}`))
            }
          }
          console.log('=== END CHANGE DETECTION ===')
          
          triggerAutoSave()
        }
      },
      { deep: true, flush: 'post' }
    )

    // Save before page unload
    const handleBeforeUnload = (event) => {
      if (hasUnsavedChanges.value) {
        console.log('Page unload detected with unsaved changes, attempting to save...')
        event.preventDefault()
        forceSave() // Attempt to save
        return event.returnValue = 'You have unsaved changes. Are you sure you want to leave?'
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)

    // Cleanup function
    return () => {
      console.log('Cleaning up autosave watchers...')
      window.removeEventListener('beforeunload', handleBeforeUnload)
      if (saveTimeout.value) {
        clearTimeout(saveTimeout.value)
      }
    }
  }

  /**
   * Load test data for development
   */
  const loadTestData = () => {
    try {
      console.log('Loading test data from defaultForm...')
      console.log('Raw defaultForm data has keys:', Object.keys(defaultForm))
      console.log('DefaultForm section toggles:', {
        includeProjects: defaultForm.includeProjects,
        includeCertifications: defaultForm.includeCertifications, 
        includeLanguages: defaultForm.includeLanguages
      })
      console.log('DefaultForm data counts:', {
        projects: defaultForm.projects?.length,
        certifications: defaultForm.certifications?.length,
        languages: defaultForm.languages?.length
      })
      
      const normalized = normalizeApiResponse(defaultForm)
      
      console.log('Test data loaded successfully:', {
        includeProjects: normalized.includeProjects,
        includeCertifications: normalized.includeCertifications,
        includeLanguages: normalized.includeLanguages,
        projectsCount: normalized.projects?.length,
        certificationsCount: normalized.certifications?.length,
        languagesCount: normalized.languages?.length
      })
      
      // Validate that test data doesn't introduce null values unexpectedly
      validateDataIntegrity(normalized, 'loadTestData')
      
      return normalized
    } catch (error) {
      console.warn('Could not load test data, using empty structure:', error)
      return createEmptyFormStructure()
    }
  }

  /**
   * Validate data integrity and log any issues
   */
  const validateDataIntegrity = (data, context = 'unknown') => {
    console.log(`=== DATA INTEGRITY CHECK (${context}) ===`)
    
    const issues = []
    
    // Check required fields that should never be null/empty
    const requiredFields = ['fullName', 'email', 'targetJobTitle', 'industry']
    requiredFields.forEach(field => {
      if (!data[field] || data[field].trim() === '') {
        issues.push(`Required field '${field}' is empty or null`)
      }
    })
    
    // Check array fields that should always be arrays
    const arrayFields = ['skills', 'workExperience', 'education', 'projects', 'certifications', 'languages', 'focusKeywords']
    arrayFields.forEach(field => {
      if (!Array.isArray(data[field])) {
        issues.push(`Array field '${field}' is not an array: ${typeof data[field]}`)
      }
    })
    
    // Check boolean fields
    const booleanFields = ['includeProjects', 'includeCertifications', 'includeLanguages', 'useAI']
    booleanFields.forEach(field => {
      if (typeof data[field] !== 'boolean') {
        issues.push(`Boolean field '${field}' is not boolean: ${typeof data[field]} (${data[field]})`)
      }
    })
    
    // Check for unexpected null values in nested objects
    if (Array.isArray(data.workExperience)) {
      data.workExperience.forEach((exp, index) => {
        if (!exp.title || !exp.company) {
          issues.push(`Work experience ${index} missing required title or company`)
        }
      })
    }
    
    if (Array.isArray(data.education)) {
      data.education.forEach((edu, index) => {
        if (!edu.degree || !edu.school) {
          issues.push(`Education ${index} missing required degree or school`)
        }
      })
    }
    
    if (issues.length > 0) {
      console.warn('Data integrity issues found:')
      issues.forEach(issue => console.warn(`- ${issue}`))
    } else {
      console.log('Data integrity check passed')
    }
    
    console.log(`=== END DATA INTEGRITY CHECK (${context}) ===`)
    return issues
  }

  /**
   * Validate form data
   */
  const validateFormData = (data) => {
    const errors = []

    if (!data.fullName?.trim()) errors.push('Full name is required')
    if (!data.email?.trim()) errors.push('Email is required')
    if (!data.title?.trim()) errors.push('Resume title is required')
    if (!data.targetJobTitle?.trim()) errors.push('Target job title is required')
    if (!data.industry?.trim()) errors.push('Industry is required')

    if (data.email?.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email.trim())) {
      errors.push('Please enter a valid email address')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  // Computed properties
  const isEditMode = computed(() => {
    return isBrowser && localStorage.getItem('editMode') === 'true'
  })

  const currentResumeId = computed(() => {
    return isBrowser ? localStorage.getItem('currentResumeId') : null
  })

  const autoSaveStatus = computed(() => {
    if (isAutoSaving.value) return 'saving'
    if (autoSaveError.value) return 'error'
    if (hasUnsavedChanges.value) return 'pending'
    if (lastSaved.value) return 'saved'
    return 'idle'
  })

  const lastSavedText = computed(() => {
    if (!lastSaved.value) return null
    
    const now = Date.now()
    const savedTime = lastSaved.value.getTime()
    const diffSeconds = Math.floor((now - savedTime) / 1000)
    
    if (diffSeconds < 60) return 'Saved just now'
    if (diffSeconds < 3600) return `Saved ${Math.floor(diffSeconds / 60)} minutes ago`
    return `Saved at ${lastSaved.value.toLocaleTimeString()}`
  })

  /**
   * Fix null/undefined values in resume data
   */
  const fixNullValues = () => {
    if (!resumeData.value) return
    
    console.log('=== FIXING NULL VALUES ===')
    const issues = validateDataIntegrity(resumeData.value, 'beforeFix')
    
    if (issues.length === 0) {
      console.log('No issues found to fix')
      return
    }
    
    // Create a fixed version
    const fixed = createEmptyFormStructure()
    
    // Copy over valid values from current data
    Object.keys(fixed).forEach(key => {
      if (resumeData.value[key] !== null && resumeData.value[key] !== undefined) {
        if (typeof resumeData.value[key] === 'string' && resumeData.value[key].trim() !== '') {
          fixed[key] = resumeData.value[key]
        } else if (typeof resumeData.value[key] !== 'string') {
          fixed[key] = resumeData.value[key]
        }
      }
    })
    
    // Ensure arrays are properly structured
    if (!Array.isArray(fixed.skills)) fixed.skills = []
    if (!Array.isArray(fixed.projects)) fixed.projects = []
    if (!Array.isArray(fixed.certifications)) fixed.certifications = []
    if (!Array.isArray(fixed.languages)) fixed.languages = []
    
    // Update the reactive data
    resumeData.value = fixed
    
    console.log('Null values fixed')
    validateDataIntegrity(resumeData.value, 'afterFix')
    console.log('=== END FIXING NULL VALUES ===')
  }

  return {
    // State
    resumeData,
    isLoading,
    error,
    
    // Autosave state
    isAutoSaving,
    lastSaved,
    isDirty,
    autoSaveError,
    hasUnsavedChanges,
    autoSaveStatus,
    lastSavedText,
    
    // Computed
    isEditMode,
    currentResumeId,
    
    // Methods
    createEmptyFormStructure,
    normalizeApiResponse,
    toApiPayload,
    loadFromStorage,
    saveToStorage,
    clearStorage,
    initializeFormData,
    validateFormData,
    validateDataIntegrity,
    fixNullValues,
    cleanObject,
    
    // Autosave methods
    triggerAutoSave,
    forceSave,
    setAutoSaveEnabled,
    updateAutoSaveConfig,
    setupAutoSaveWatcher
  }
}