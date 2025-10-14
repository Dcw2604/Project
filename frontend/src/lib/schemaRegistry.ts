/**
 * Schema Discovery Utility
 * Discovers available list endpoints from OpenAPI schema
 */

interface SchemaEndpoint {
  path: string
  method: string
  summary?: string
  description?: string
}

interface SchemaRegistry {
  documents: SchemaEndpoint | null
  exams: SchemaEndpoint | null
  loaded: boolean
}

class SchemaRegistryManager {
  private registry: SchemaRegistry = {
    documents: null,
    exams: null,
    loaded: false
  }

  private sessionUploads: Array<{ label: string; document_id: string | number }> = []

  async loadSchema(): Promise<void> {
    if (this.registry.loaded) return

    try {
      const response = await fetch('/api/schema/')
      if (!response.ok) throw new Error('Failed to fetch schema')
      
      const schema = await response.json()
      this.discoverEndpoints(schema)
      this.registry.loaded = true
    } catch (error) {
      console.warn('Failed to load schema, using fallback discovery:', error)
      this.registry.loaded = true
    }
  }

  private sessionExams: Array<{ title: string; exam_id: string | number; created_at: string }> = []

  // Add these methods
  addSessionExam(title: string, exam_id: string | number): void {
    this.sessionExams.push({ 
      title, 
      exam_id, 
      created_at: new Date().toISOString() 
    })
  }
  
  getSessionExams(): Array<{ title: string; exam_id: string | number; created_at: string }> {
    return [...this.sessionExams]
  }
  
  clearSessionExams(): void {
    this.sessionExams = []
  }

  private discoverEndpoints(schema: any): void {
    const paths = schema.paths || {}
    
    // Find documents list endpoint
    this.registry.documents = this.findListEndpoint(paths, 'documents')
    
    // Find exams list endpoint  
    this.registry.exams = this.findListEndpoint(paths, 'exams')
  }

  findListEndpoint(paths: any, kind: 'documents' | 'exams'): SchemaEndpoint | null {
    const candidates: Array<{ path: string; method: string; priority: number }> = []
    
    for (const [path, methods] of Object.entries(paths)) {
      if (!path.includes(`/${kind}`)) continue
      
      for (const [method, details] of Object.entries(methods as any)) {
        if (method.toUpperCase() !== 'GET') continue
        
        let priority = 0
        
        // Prefer paths with specific keywords
        if (path.includes('available') || path.includes('assigned') || path.includes('mine')) {
          priority += 10
        }
        
        // Prefer index endpoints
        if (path.endsWith('/') || path.endsWith(`/${kind}`)) {
          priority += 5
        }
        
        // Prefer shorter paths
        priority += Math.max(0, 10 - path.split('/').length)
        
        candidates.push({ path, method, priority })
      }
    }
    
    if (candidates.length === 0) return null
    
    // Sort by priority and return the best match
    candidates.sort((a, b) => b.priority - a.priority)
    const best = candidates[0]
    
    return {
      path: best.path,
      method: best.method,
      summary: `Discovered ${kind} list endpoint`
    }
  }

  async findListEndpointByKind(kind: 'documents' | 'exams'): Promise<SchemaEndpoint | null> {
    await this.loadSchema()
    return this.registry[kind]
  }

  // Session uploads management
  addSessionUpload(label: string, document_id: string | number): void {
    this.sessionUploads.push({ label, document_id })
  }

  getSessionUploads(): Array<{ label: string; document_id: string | number }> {
    return [...this.sessionUploads]
  }

  clearSessionUploads(): void {
    this.sessionUploads = []
  }

  // Check if we have any list endpoints
  hasListEndpoints(): boolean {
    return this.registry.documents !== null || this.registry.exams !== null
  }

  // Get discovery status
  getDiscoveryStatus(): {
    documents: boolean
    exams: boolean
    hasAny: boolean
  } {
    return {
      documents: this.registry.documents !== null,
      exams: this.registry.exams !== null,
      hasAny: this.hasListEndpoints()
    }
  }
}

export const schemaRegistry = new SchemaRegistryManager()
export type { SchemaEndpoint }
