import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface IndexRequest {
  repo_url: string;
}

export interface IndexResponse {
  status: string;
  message: string;
  chunks_count: number;
}

export interface QueryRequest {
  query: string;
  top_k?: number;
}

export interface QueryResponse {
  answer: string;
  sources: Array<{
    file_path: string;
    start_line: number;
    end_line: number;
    chunk_index: number;
  }>;
}

export interface CollectionStats {
  count: number;
  name: string;
}

export interface IndexStatus {
  status: string;
  progress: number;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class RagService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  indexRepository(repoUrl: string): Observable<IndexResponse> {
    const request: IndexRequest = { repo_url: repoUrl };
    return this.http.post<IndexResponse>(`${this.apiUrl}/index`, request);
  }

  queryCodebase(query: string, topK: number = 5): Observable<QueryResponse> {
    const request: QueryRequest = { query, top_k: topK };
    return this.http.post<QueryResponse>(`${this.apiUrl}/query`, request);
  }

  getIndexStatus(): Observable<IndexStatus> {
    return this.http.get<IndexStatus>(`${this.apiUrl}/status`);
  }

  getCollectionStats(): Observable<CollectionStats> {
    return this.http.get<CollectionStats>(`${this.apiUrl}/collections`);
  }

  clearVectorStore(): Observable<any> {
    return this.http.post(`${this.apiUrl}/clear`, {});
  }

  healthCheck(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }
}
