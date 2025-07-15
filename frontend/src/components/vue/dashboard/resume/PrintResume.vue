<template>
  <div class="print-container">
    <!-- Print Header (only visible when printing) -->
    <div class="print-only print-header">
      <div class="print-timestamp">
        Generated on {{ new Date().toLocaleDateString() }}
      </div>
    </div>

    <!-- Resume Content for Print -->
    <div class="resume-content" ref="printContent">
      <!-- Header Section -->
      <header class="resume-header">
        <h1 class="name">{{ getContactInfo().name || "Resume" }}</h1>

        <!-- Contact Information -->
        <div class="contact-info">
          <div class="contact-row">
            <span v-if="getContactInfo().email" class="contact-item">
              {{ getContactInfo().email }}
            </span>
            <span v-if="getContactInfo().phone" class="contact-item">
              {{ getContactInfo().phone }}
            </span>
          </div>
          <div class="contact-row">
            <span v-if="getContactInfo().location" class="contact-item">
              {{ getContactInfo().location }}
            </span>
            <span v-if="getContactInfo().linkedin" class="contact-item">
              {{ getContactInfo().linkedin }}
            </span>
          </div>
        </div>
      </header>

      <!-- Professional Summary -->
      <section v-if="resumeData.sections?.professional_summary" class="section">
        <h2 class="section-title">PROFESSIONAL SUMMARY</h2>
        <div class="section-content">
          <p class="summary-text">{{ resumeData.sections.professional_summary }}</p>
        </div>
      </section>

      <!-- Core Competencies -->
      <section v-if="resumeData.sections?.core_competencies?.length" class="section">
        <h2 class="section-title">CORE COMPETENCIES</h2>
        <div class="section-content">
          <div class="skills-grid">
            <span
              v-for="(skill, index) in resumeData.sections.core_competencies"
              :key="`competency-${index}`"
              class="skill-item"
            >
              {{ skill }}
            </span>
          </div>
        </div>
      </section>

      <!-- Professional Experience -->
      <section v-if="resumeData.sections?.experience?.length" class="section">
        <h2 class="section-title">PROFESSIONAL EXPERIENCE</h2>
        <div class="section-content">
          <div
            v-for="(exp, index) in resumeData.sections.experience"
            :key="`exp-${index}`"
            class="experience-item"
          >
            <div class="experience-header">
              <div class="job-info">
                <h3 class="job-title">{{ exp.title }}</h3>
                <p class="company">{{ exp.company }}</p>
                <p v-if="exp.location" class="location">{{ exp.location }}</p>
              </div>
              <div class="date-info">
                <p class="dates">
                  {{ formatDateRange(exp.startDate, exp.endDate, exp.current) }}
                </p>
              </div>
            </div>

            <!-- Achievements -->
            <div v-if="exp.achievements?.length" class="achievements">
              <ul class="achievement-list">
                <li
                  v-for="(achievement, achIndex) in exp.achievements"
                  :key="`achievement-${index}-${achIndex}`"
                  class="achievement-item"
                >
                  {{ achievement }}
                </li>
              </ul>
            </div>

            <!-- Legacy description support -->
            <div v-else-if="exp.description" class="description">
              <p>{{ exp.description }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Technical Skills -->
      <section v-if="resumeData.sections?.technical_skills" class="section">
        <h2 class="section-title">TECHNICAL SKILLS</h2>
        <div class="section-content">
          <div class="skills-categories">
            <div
              v-for="(skillList, category) in resumeData.sections.technical_skills"
              :key="category"
              class="skill-category"
            >
              <h4 class="category-title">{{ formatSkillCategory(category) }}:</h4>
              <p class="category-skills">{{ skillList.join(", ") }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Education -->
      <section v-if="resumeData.sections?.education?.length" class="section">
        <h2 class="section-title">EDUCATION</h2>
        <div class="section-content">
          <div
            v-for="(edu, index) in resumeData.sections.education"
            :key="`edu-${index}`"
            class="education-item"
          >
            <div class="education-header">
              <div class="degree-info">
                <h3 class="degree">{{ edu.degree }}</h3>
                <p class="institution">{{ edu.institution }}</p>
                <p v-if="edu.location" class="location">{{ edu.location }}</p>
                <p v-if="edu.gpa" class="gpa">GPA: {{ edu.gpa }}</p>
              </div>
              <div class="date-info">
                <p class="dates">{{ formatEducationDate(edu) }}</p>
              </div>
            </div>

            <!-- Relevant Coursework -->
            <div v-if="edu.relevant_coursework?.length" class="coursework">
              <p>
                <strong>Relevant Coursework:</strong>
                {{ edu.relevant_coursework.join(", ") }}
              </p>
            </div>

            <!-- Description -->
            <div v-if="edu.description" class="description">
              <p>{{ edu.description }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Projects -->
      <section v-if="resumeData.sections?.projects?.length" class="section">
        <h2 class="section-title">PROJECTS</h2>
        <div class="section-content">
          <div
            v-for="(project, index) in resumeData.sections.projects"
            :key="`project-${index}`"
            class="project-item"
          >
            <div class="project-header">
              <h3 class="project-title">{{ project.name || project.title }}</h3>
              <p v-if="project.url" class="project-url">{{ project.url }}</p>
            </div>

            <p v-if="project.description" class="project-description">
              {{ project.description }}
            </p>

            <!-- Technologies -->
            <div v-if="project.technologies?.length" class="technologies">
              <p><strong>Technologies:</strong> {{ project.technologies.join(", ") }}</p>
            </div>

            <!-- Outcomes -->
            <div v-if="project.outcomes" class="outcomes">
              <p><strong>Outcomes:</strong> {{ project.outcomes }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Certifications -->
      <section v-if="resumeData.sections?.certifications?.length" class="section">
        <h2 class="section-title">CERTIFICATIONS</h2>
        <div class="section-content">
          <div class="certifications-grid">
            <div
              v-for="(cert, index) in resumeData.sections.certifications"
              :key="`cert-${index}`"
              class="certification-item"
            >
              {{ cert }}
            </div>
          </div>
        </div>
      </section>

      <!-- Additional Sections -->
      <div v-if="resumeData.sections?.additional_sections">
        <!-- Languages -->
        <section
          v-if="resumeData.sections.additional_sections.languages?.length"
          class="section"
        >
          <h2 class="section-title">LANGUAGES</h2>
          <div class="section-content">
            <p>{{ resumeData.sections.additional_sections.languages.join(", ") }}</p>
          </div>
        </section>

        <!-- Awards -->
        <section
          v-if="resumeData.sections.additional_sections.awards?.length"
          class="section"
        >
          <h2 class="section-title">AWARDS & RECOGNITION</h2>
          <div class="section-content">
            <ul class="awards-list">
              <li
                v-for="(award, index) in resumeData.sections.additional_sections.awards"
                :key="`award-${index}`"
              >
                {{ award }}
              </li>
            </ul>
          </div>
        </section>

        <!-- Publications -->
        <section
          v-if="resumeData.sections.additional_sections.publications?.length"
          class="section"
        >
          <h2 class="section-title">PUBLICATIONS</h2>
          <div class="section-content">
            <ul class="publications-list">
              <li
                v-for="(publication, index) in resumeData.sections.additional_sections
                  .publications"
                :key="`pub-${index}`"
              >
                {{ publication }}
              </li>
            </ul>
          </div>
        </section>
      </div>
    </div>

    <!-- Print Controls (hidden when printing) -->
    <div class="print-controls no-print">
      <div class="controls-container">
        <button @click="printResume" class="print-button">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M5 4v3H4a2 2 0 00-2 2v3a2 2 0 002 2h1v2a2 2 0 002 2h6a2 2 0 002-2v-2h1a2 2 0 002-2V9a2 2 0 00-2-2h-1V4a2 2 0 00-2-2H7a2 2 0 00-2 2zm8 0H7v3h6V4zM5 14H4v-3h1v3zm1 0v2h6v-2H6zm0-1h6v-2H6v2z"
              clip-rule="evenodd"
            ></path>
          </svg>
          Print Resume
        </button>

        <button @click="openPrintPreview" class="preview-button">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"></path>
            <path
              fill-rule="evenodd"
              d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
              clip-rule="evenodd"
            ></path>
          </svg>
          Print Preview
        </button>

        <button @click="savePrintVersion" class="save-button">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path
              fill-rule="evenodd"
              d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z"
              clip-rule="evenodd"
            ></path>
          </svg>
          Save as PDF
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PrintResume",
  props: {
    resumeData: {
      type: Object,
      required: true,
    },
  },
  methods: {
    getContactInfo() {
      const personal = this.resumeData.sections?.personal_info || {};
      const contact = this.resumeData.sections?.contact_info || {};
      const profile = this.resumeData.profile || {};

      return {
        name: personal.name || contact.name || profile.name || "",
        email: personal.email || contact.email || profile.email || "",
        phone: personal.phone || contact.phone || profile.phone || "",
        location: personal.location || contact.location || profile.location || "",
        linkedin: personal.linkedin || contact.linkedin || profile.linkedin || "",
      };
    },

    formatSkillCategory(category) {
      return category.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase());
    },

    formatDateRange(startDate, endDate, isCurrent = false) {
      if (!startDate) return "N/A";
      const start = this.formatDate(startDate);
      const end = isCurrent || !endDate ? "Present" : this.formatDate(endDate);
      return `${start} - ${end}`;
    },

    formatDate(dateString) {
      if (!dateString) return "";
      try {
        if (typeof dateString === "number") {
          return dateString.toString();
        }

        if (dateString.includes("-")) {
          const [year, month] = dateString.split("-");
          const date = new Date(year, month - 1);
          return date.toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
          });
        }

        return dateString;
      } catch {
        return dateString;
      }
    },

    formatEducationDate(edu) {
      if (edu.graduation_date) {
        return this.formatDate(edu.graduation_date);
      }

      if (edu.endYear) {
        return edu.startYear
          ? `${edu.startYear} - ${edu.endYear}`
          : edu.endYear.toString();
      }

      return edu.startYear ? edu.startYear.toString() : "N/A";
    },

    printResume() {
      // Trigger browser print dialog
      window.print();
    },

    openPrintPreview() {
      // Open print preview in new window
      const printWindow = window.open("", "_blank");
      const printContent = this.$refs.printContent.innerHTML;

      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Resume Print Preview</title>
          <style>
            ${this.getPrintStyles()}
          </style>
        </head>
        <body>
          <div class="print-container">
            ${printContent}
          </div>
        </body>
        </html>
      `);

      printWindow.document.close();
      printWindow.focus();
    },

    savePrintVersion() {
      // Create a blob with the resume content and trigger download
      const printContent = this.$refs.printContent.innerHTML;
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <title>Resume</title>
          <style>
            ${this.getPrintStyles()}
          </style>
        </head>
        <body>
          <div class="print-container">
            ${printContent}
          </div>
        </body>
        </html>
      `;

      const blob = new Blob([htmlContent], { type: "text/html" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${this.getContactInfo().name || "resume"}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },

    getPrintStyles() {
      return `
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: 'Times New Roman', Times, serif;
          font-size: 11pt;
          line-height: 1.3;
          color: #000;
          background: white;
        }

        .print-container {
          max-width: 8.5in;
          margin: 0 auto;
          padding: 0.5in;
        }

        .resume-header {
          text-align: center;
          margin-bottom: 20pt;
          border-bottom: 1pt solid #000;
          padding-bottom: 10pt;
        }

        .name {
          font-size: 18pt;
          font-weight: bold;
          margin-bottom: 8pt;
          text-transform: uppercase;
          letter-spacing: 1pt;
        }

        .contact-info {
          font-size: 10pt;
        }

        .contact-row {
          margin-bottom: 3pt;
        }

        .contact-item {
          margin: 0 10pt;
        }

        .section {
          margin-bottom: 15pt;
          page-break-inside: avoid;
        }

        .section-title {
          font-size: 12pt;
          font-weight: bold;
          text-transform: uppercase;
          border-bottom: 1pt solid #000;
          margin-bottom: 8pt;
          padding-bottom: 2pt;
          letter-spacing: 0.5pt;
        }

        .section-content {
          margin-left: 5pt;
        }

        .experience-item,
        .education-item,
        .project-item {
          margin-bottom: 12pt;
          page-break-inside: avoid;
        }

        .experience-header,
        .education-header,
        .project-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 5pt;
        }

        .job-title,
        .degree,
        .project-title {
          font-size: 11pt;
          font-weight: bold;
          margin-bottom: 2pt;
        }

        .company,
        .institution {
          font-weight: bold;
          font-style: italic;
        }

        .location,
        .dates,
        .gpa {
          font-size: 10pt;
          color: #333;
        }

        .achievement-list,
        .awards-list,
        .publications-list {
          margin-left: 15pt;
          margin-top: 5pt;
        }

        .achievement-item {
          margin-bottom: 3pt;
          text-align: justify;
        }

        .skills-grid {
          display: flex;
          flex-wrap: wrap;
          gap: 8pt;
        }

        .skill-item {
          font-size: 10pt;
          padding: 2pt 6pt;
          border: 1pt solid #000;
          border-radius: 3pt;
        }

        .skills-categories {
          margin-top: 5pt;
        }

        .skill-category {
          margin-bottom: 8pt;
        }

        .category-title {
          font-weight: bold;
          display: inline;
        }

        .category-skills {
          display: inline;
          margin-left: 5pt;
        }

        .certifications-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200pt, 1fr));
          gap: 5pt;
        }

        .certification-item {
          font-size: 10pt;
          padding: 3pt;
          border: 1pt solid #ccc;
          text-align: center;
        }

        .summary-text {
          text-align: justify;
          margin-bottom: 5pt;
        }

        .project-description,
        .description {
          margin-bottom: 5pt;
          text-align: justify;
        }

        .technologies,
        .outcomes,
        .coursework {
          font-size: 10pt;
          margin-top: 5pt;
        }

        /* Page break controls */
        .section:last-child {
          margin-bottom: 0;
        }

        @page {
          margin: 0.5in;
          size: letter;
        }

        /* Ensure content doesn't break awkwardly */
        h2, h3, h4 {
          page-break-after: avoid;
        }

        ul, ol {
          page-break-inside: avoid;
        }
      `;
    },
  },
};
</script>

<style scoped>
/* Screen styles */
.print-container {
  @apply max-w-4xl mx-auto bg-white;
}

.resume-content {
  @apply p-8;
}

.resume-header {
  @apply text-center mb-6 pb-4 border-b-2 border-gray-800;
}

.name {
  @apply text-2xl font-bold mb-2 uppercase tracking-wide;
}

.contact-info {
  @apply text-sm text-gray-700;
}

.contact-row {
  @apply mb-1;
}

.contact-item {
  @apply mx-2;
}

.section {
  @apply mb-6;
}

.section-title {
  @apply text-lg font-bold uppercase border-b border-gray-800 mb-3 pb-1 tracking-wide;
}

.section-content {
  @apply ml-2;
}

.experience-item,
.education-item,
.project-item {
  @apply mb-4;
}

.experience-header,
.education-header,
.project-header {
  @apply flex justify-between items-start mb-2;
}

.job-title,
.degree,
.project-title {
  @apply font-bold mb-1;
}

.company,
.institution {
  @apply font-semibold italic;
}

.location,
.dates,
.gpa {
  @apply text-sm text-gray-600;
}

.achievement-list,
.awards-list,
.publications-list {
  @apply ml-6 mt-2 space-y-1;
}

.achievement-item {
  @apply leading-relaxed;
}

.skills-grid {
  @apply flex flex-wrap gap-2;
}

.skill-item {
  @apply text-xs px-2 py-1 border border-gray-800 rounded;
}

.skills-categories {
  @apply mt-2;
}

.skill-category {
  @apply mb-3;
}

.category-title {
  @apply font-semibold;
}

.category-skills {
  @apply ml-2;
}

.certifications-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-2;
}

.certification-item {
  @apply text-sm p-2 border border-gray-300 text-center;
}

.summary-text {
  @apply leading-relaxed mb-2;
}

.project-description,
.description {
  @apply mb-2 leading-relaxed;
}

.technologies,
.outcomes,
.coursework {
  @apply text-sm mt-2;
}

/* Print Controls */
.print-controls {
  @apply fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 border;
}

.controls-container {
  @apply flex flex-col space-y-2;
}

.print-button,
.preview-button,
.save-button {
  @apply flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors;
}

.print-button {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.preview-button {
  @apply bg-gray-600 text-white hover:bg-gray-700;
}

.save-button {
  @apply bg-green-600 text-white hover:bg-green-700;
}

/* Print-specific styles */
@media print {
  .no-print {
    display: none !important;
  }

  .print-only {
    display: block !important;
  }

  .print-container {
    @apply max-w-none m-0 p-4;
  }

  .resume-content {
    @apply p-0;
  }

  * {
    @apply text-black;
  }

  .resume-header {
    @apply border-b-2 border-black;
  }

  .section-title {
    @apply border-b border-black;
  }

  .skill-item {
    @apply border-black;
  }

  /* Ensure proper page breaks */
  .section {
    page-break-inside: avoid;
  }

  .experience-item,
  .education-item,
  .project-item {
    page-break-inside: avoid;
  }

  /* Hide unnecessary elements */
  .print-controls {
    display: none !important;
  }
}

.print-only {
  display: none;
}

.print-header {
  @apply text-right text-xs text-gray-500 mb-4;
}

.print-timestamp {
  @apply italic;
}
</style>
