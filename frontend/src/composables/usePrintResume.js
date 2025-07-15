export const usePrintResume = (resumeData) => {

  const printResume = () => {
    const printWindow = window.open('', '_blank', 'width=800,height=1000');
    const printContent = generatePrintHTML();
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.onload = () => {
      printWindow.focus();
      setTimeout(() => printWindow.print(), 250);
    };
  };

  const generatePrintHTML = () => {
    const contactInfo = getContactInfo();
    const currentDate = new Date().toLocaleDateString();
    return `
<!DOCTYPE html>
<html>
<head>
  <title>Resume - ${contactInfo.name || 'Resume'}</title>
  <style>${getPrintStyles()}</style>
</head>
<body>
  <div class="print-container">
    ${generateHeader(contactInfo)}
    ${generatePrintSections()}
    <div class="print-footer"><p>Generated on ${currentDate}</p></div>
  </div>
</body>
</html>`;
  };

  const getContactInfo = () => resumeData.contact || {};

  const formatDateRange = (start, end, isCurrent) => {
    if (!start) return '';
    const startDate = new Date(start).toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
    const endDate = isCurrent ? 'Present' : (end ? new Date(end).toLocaleDateString(undefined, { month: 'short', year: 'numeric' }) : '');
    return `${startDate} - ${endDate}`;
  };

  const formatEducationDate = (edu) => {
    return formatDateRange(edu.startDate, edu.endDate, edu.current);
  };

  const formatSkillCategory = (label) => label.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

  const generateHeader = (contactInfo) => `
<header class="resume-header">
  <h1 class="name">${contactInfo.name || 'Resume'}</h1>
  <div class="contact-info">
    ${contactInfo.email ? `<span class="contact-item">${contactInfo.email}</span>` : ''}
    ${contactInfo.phone ? `<span class="contact-item">${contactInfo.phone}</span>` : ''}
    ${contactInfo.location ? `<span class="contact-item">${contactInfo.location}</span>` : ''}
    ${contactInfo.linkedin ? `<span class="contact-item">${contactInfo.linkedin}</span>` : ''}
  </div>
</header>`;

  const generatePrintSections = () => {
    let sections = '';
    const sec = resumeData.sections || {};

    if (sec.professional_summary) {
      sections += sectionBlock('Professional Summary', `<p class="summary-text">${sec.professional_summary}</p>`);
    }

    if (sec.core_competencies?.length) {
      const items = sec.core_competencies.map(skill => `<span class="skill-item">${skill}</span>`).join('');
      sections += sectionBlock('Core Competencies', `<div class="skills-grid">${items}</div>`);
    }

    if (sec.experience?.length) {
      const items = sec.experience.map(exp => {
        const achievements = exp.achievements?.length
          ? `<ul class="achievement-list">${exp.achievements.map(a => `<li class="achievement-item">${a}</li>`).join('')}</ul>`
          : (exp.description ? `<div class="description"><p>${exp.description}</p></div>` : '');
        return `
<div class="experience-item">
  <div class="experience-header">
    <div class="job-info">
      <h3 class="job-title">${exp.title}</h3>
      <p class="company">${exp.company}</p>
      ${exp.location ? `<p class="location">${exp.location}</p>` : ''}
    </div>
    <div class="date-info">
      <p class="dates">${formatDateRange(exp.startDate, exp.endDate, exp.current)}</p>
    </div>
  </div>
  ${achievements}
</div>`;
      }).join('');
      sections += sectionBlock('Professional Experience', items);
    }

    if (sec.technical_skills) {
      const categories = Object.entries(sec.technical_skills).map(
        ([cat, list]) => `<div class="skill-category">
          <h4 class="category-title">${formatSkillCategory(cat)}:</h4>
          <p class="category-skills">${list.join(', ')}</p>
        </div>`
      ).join('');
      sections += sectionBlock('Technical Skills', `<div class="skills-categories">${categories}</div>`);
    }

    if (sec.education?.length) {
      const items = sec.education.map(edu => {
        const cw = edu.relevant_coursework?.length ? `<div class="coursework"><p><strong>Relevant Coursework:</strong> ${edu.relevant_coursework.join(', ')}</p></div>` : '';
        const desc = edu.description ? `<div class="description"><p>${edu.description}</p></div>` : '';
        return `
<div class="education-item">
  <div class="education-header">
    <div class="degree-info">
      <h3 class="degree">${edu.degree}</h3>
      <p class="institution">${edu.institution}</p>
      ${edu.location ? `<p class="location">${edu.location}</p>` : ''}
      ${edu.gpa ? `<p class="gpa">GPA: ${edu.gpa}</p>` : ''}
    </div>
    <div class="date-info">
      <p class="dates">${formatEducationDate(edu)}</p>
    </div>
  </div>
  ${cw}
  ${desc}
</div>`;
      }).join('');
      sections += sectionBlock('Education', items);
    }

    if (sec.projects?.length) {
      const items = sec.projects.map(p => `
<div class="project-item">
  <div class="project-header">
    <h3 class="project-title">${p.name || p.title}</h3>
    ${p.url ? `<p class="project-url">${p.url}</p>` : ''}
  </div>
  ${p.description ? `<p class="project-description">${p.description}</p>` : ''}
  ${p.technologies?.length ? `<div class="technologies"><p><strong>Technologies:</strong> ${p.technologies.join(', ')}</p></div>` : ''}
  ${p.outcomes ? `<div class="outcomes"><p><strong>Outcomes:</strong> ${p.outcomes}</p></div>` : ''}
</div>`).join('');
      sections += sectionBlock('Projects', items);
    }

    if (sec.certifications?.length) {
      const certs = sec.certifications.map(cert => `<div class="certification-item">${cert}</div>`).join('');
      sections += sectionBlock('Certifications', `<div class="certifications-grid">${certs}</div>`);
    }

    if (sec.additional_sections) {
      const add = sec.additional_sections;

      if (add.languages?.length) {
        sections += sectionBlock('Languages', `<p>${add.languages.join(', ')}</p>`);
      }

      if (add.awards?.length) {
        sections += sectionBlock('Awards & Recognition', `<ul class="awards-list">${add.awards.map(a => `<li>${a}</li>`).join('')}</ul>`);
      }

      if (add.publications?.length) {
        sections += sectionBlock('Publications', `<ul class="publications-list">${add.publications.map(p => `<li>${p}</li>`).join('')}</ul>`);
      }
    }

    return sections;
  };

  const sectionBlock = (title, content) => `
<section class="section">
  <h2 class="section-title">${title.toUpperCase()}</h2>
  <div class="section-content">${content}</div>
</section>`;

  const getPrintStyles = () => {
    return `/* Your long CSS goes here */`;
  };

  return {
    printResume
  };
};
