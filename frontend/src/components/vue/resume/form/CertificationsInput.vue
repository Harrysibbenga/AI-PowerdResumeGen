<template>
  <div class="bg-white p-6 rounded-lg border border-gray-200">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">Certifications</h3>
      <button
        type="button"
        @click="addCertification()"
        class="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        + Add Certification
      </button>
    </div>

    <!-- Suggested Certifications -->
    <div v-if="industry && suggestions.length" class="mb-6">
      <p class="text-sm font-medium text-gray-700 mb-3">
        Suggested certifications for {{ industryName }}:
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="cert in suggestions"
          :key="cert"
          type="button"
          @click="addSuggestedCertification(cert)"
          class="px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 border border-blue-200 transition-colors"
        >
          + {{ cert }}
        </button>
      </div>
    </div>

    <!-- Certifications List -->
    <div v-if="certifications.length > 0" class="space-y-4">
      <div 
        v-for="(cert, index) in certifications" 
        :key="index" 
        class="bg-gray-50 p-4 rounded-lg border border-gray-200"
      >
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Certification Name -->
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Certification Name *
            </label>
            <input
              v-model="cert.name"
              type="text"
              placeholder="e.g., AWS Certified Solutions Architect"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @input="updateCertification(index, cert)"
              required
            />
          </div>

          <!-- Remove Button -->
          <div class="flex items-end justify-end md:justify-start">
            <button
              type="button"
              @click="removeCertification(index)"
              class="px-3 py-2 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors"
              title="Remove certification"
            >
              <i class="pi pi-trash"></i> Remove
            </button>
          </div>

          <!-- Issuer -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Issuing Organization
            </label>
            <input
              v-model="cert.issuer"
              type="text"
              placeholder="e.g., Amazon Web Services"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @input="updateCertification(index, cert)"
            />
          </div>

          <!-- Date -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Date Obtained
            </label>
            <input
              v-model="cert.date"
              type="month"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @input="updateCertification(index, cert)"
              placeholder="YYYY-MM"
            />
            <p class="text-xs text-gray-500 mt-1">Format: YYYY-MM (e.g., 2023-06)</p>
          </div>

          <!-- Expiry Date (Optional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Expiry Date
            </label>
            <input
              v-model="cert.expiryDate"
              type="month"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @input="updateCertification(index, cert)"
              placeholder="YYYY-MM"
            />
            <p class="text-xs text-gray-500 mt-1">Format: YYYY-MM (if applicable)</p>
          </div>
        </div>

        <!-- Credential ID/URL (Optional) -->
        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Credential ID or Verification URL
          </label>
          <input
            v-model="cert.credentialId"
            type="text"
            placeholder="e.g., Credential ID or link to verify certification"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            @input="updateCertification(index, cert)"
          />
          <p class="text-xs text-gray-500 mt-1">Optional - helps employers verify your certification</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
      <i class="pi pi-certificate text-4xl text-gray-400 mb-2"></i>
      <p class="text-gray-600 font-medium">No certifications added yet</p>
      <p class="text-gray-500 text-sm mt-1">Click "Add Certification" or select from suggestions above</p>
    </div>
  </div>
</template>

<script>
import { getCertificationSuggestions, getIndustryById } from "@/utils/industries.js";

export default {
  name: "CertificationsInput",
  props: {
    modelValue: { type: Array, required: true },
    industry: { type: String, required: true },
  },
  emits: ["update:modelValue", "change"],
  computed: {
    suggestions() {
      return this.industry ? getCertificationSuggestions(this.industry) : [];
    },
    industryName() {
      const industry = getIndustryById(this.industry);
      return industry?.name || "";
    },
    certifications() {
      // Ensure all items are objects with proper structure
      return this.modelValue.map(cert => {
        if (typeof cert === 'string') {
          return {
            name: cert,
            issuer: '',
            date: '',
            expiryDate: '',
            credentialId: ''
          };
        }
        return {
          name: cert.name || '',
          issuer: cert.issuer || '',
          date: cert.date || '',
          expiryDate: cert.expiryDate || cert.expiry_date || '',
          credentialId: cert.credentialId || cert.credential_id || ''
        };
      }).filter(cert => cert.name.trim() !== '' || this.modelValue.length === 0);
    }
  },
  mounted() {
    console.log('CertificationsInput mounted with modelValue:', this.modelValue);
    // Ensure we have proper object structure
    this.normalizeCertifications();
  },
  methods: {
    normalizeCertifications() {
      // Convert any string certifications to object format
      const normalized = this.modelValue.map(cert => {
        if (typeof cert === 'string' && cert.trim() !== '') {
          return {
            name: cert.trim(),
            issuer: '',
            date: '',
            expiryDate: '',
            credentialId: ''
          };
        } else if (typeof cert === 'object' && cert !== null) {
          return {
            name: cert.name || '',
            issuer: cert.issuer || '',
            date: cert.date || '',
            expiryDate: cert.expiryDate || cert.expiry_date || '',
            credentialId: cert.credentialId || cert.credential_id || ''
          };
        }
        return null;
      }).filter(cert => cert !== null);

      if (normalized.length === 0) {
        // Start with one empty certification
        normalized.push({
          name: '',
          issuer: '',
          date: '',
          expiryDate: '',
          credentialId: ''
        });
      }

      if (JSON.stringify(normalized) !== JSON.stringify(this.modelValue)) {
        console.log('Normalizing certifications from:', this.modelValue, 'to:', normalized);
        this.$emit("update:modelValue", normalized);
        this.$emit("change");
      }
    },
    addCertification() {
      const newCert = {
        name: '',
        issuer: '',
        date: '',
        expiryDate: '',
        credentialId: ''
      };
      
      const updated = [...this.modelValue, newCert];
      console.log('Adding new certification:', newCert);
      this.$emit("update:modelValue", updated);
      this.$emit("change");
    },
    addSuggestedCertification(certName) {
      // Check if certification already exists
      const exists = this.certifications.some(cert => 
        cert.name.toLowerCase() === certName.toLowerCase()
      );
      
      if (!exists) {
        const newCert = {
          name: certName,
          issuer: '',
          date: '',
          expiryDate: '',
          credentialId: ''
        };

        // Replace first empty certification or add new one
        const updated = [...this.modelValue];
        const firstEmptyIndex = updated.findIndex(cert => 
          (typeof cert === 'string' && cert === '') || 
          (typeof cert === 'object' && (!cert.name || cert.name.trim() === ''))
        );

        if (firstEmptyIndex !== -1) {
          updated[firstEmptyIndex] = newCert;
        } else {
          updated.push(newCert);
        }

        console.log('Adding suggested certification:', certName);
        this.$emit("update:modelValue", updated);
        this.$emit("change");
      }
    },
    removeCertification(index) {
      const updated = [...this.modelValue];
      updated.splice(index, 1);
      
      // Ensure at least one empty certification remains
      if (updated.length === 0) {
        updated.push({
          name: '',
          issuer: '',
          date: '',
          expiryDate: '',
          credentialId: ''
        });
      }
      
      console.log('Removing certification at index:', index);
      this.$emit("update:modelValue", updated);
      this.$emit("change");
    },
    updateCertification(index, cert) {
      const updated = [...this.modelValue];
      
      // Ensure date format is YYYY-MM
      const updatedCert = { ...cert };
      if (updatedCert.date) {
        updatedCert.date = this.normalizeDate(updatedCert.date);
      }
      if (updatedCert.expiryDate) {
        updatedCert.expiryDate = this.normalizeDate(updatedCert.expiryDate);
      }
      
      updated[index] = updatedCert;
      
      console.log('Updating certification at index:', index, 'with:', updatedCert);
      this.$emit("update:modelValue", updated);
      this.$emit("change");
    },
    
    normalizeDate(dateInput) {
      // Handle various input formats and normalize to YYYY-MM
      if (!dateInput) return '';
      
      const dateStr = dateInput.toString().trim();
      
      // If already in YYYY-MM format, return as-is
      if (/^\d{4}-\d{2}$/.test(dateStr)) {
        return dateStr;
      }
      
      // Handle MM-DD-YYYY format
      if (/^\d{2}-\d{2}-\d{4}$/.test(dateStr)) {
        const [month, day, year] = dateStr.split('-');
        return `${year}-${month}`;
      }
      
      // Handle DD-MM-YYYY format  
      if (/^\d{2}-\d{2}-\d{4}$/.test(dateStr)) {
        const [day, month, year] = dateStr.split('-');
        return `${year}-${month}`;
      }
      
      // Handle YYYY-MM-DD format (extract year-month)
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
        return dateStr.substring(0, 7); // Extract YYYY-MM
      }
      
      // Handle MM/YYYY format
      if (/^\d{2}\/\d{4}$/.test(dateStr)) {
        const [month, year] = dateStr.split('/');
        return `${year}-${month}`;
      }
      
      // If we can't parse it, return original
      console.warn('Could not normalize date format:', dateStr);
      return dateStr;
    },
    
    formatDateForDisplay(dateStr) {
      // Convert YYYY-MM to readable format for display
      if (!dateStr || !/^\d{4}-\d{2}$/.test(dateStr)) return dateStr;
      
      const [year, month] = dateStr.split('-');
      const date = new Date(parseInt(year), parseInt(month) - 1);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
    }
  },
};
</script>
