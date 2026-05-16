import { Component, OnInit } from '@angular/core';
import { RagService, QueryResponse } from '../../services/rag.service';

interface Message {
  type: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    file_path: string;
    filename: string;
    start_line: number;
    end_line: number;
    chunk_index: number;
    score: number;
  }>;
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit {
  messages: Message[] = [];
  inputMessage = '';
  isLoading = false;
  collectionCount = 0;

  constructor(private ragService: RagService) { }

  ngOnInit() {
    this.loadCollectionStats();
  }

  sendMessage() {
    if (!this.inputMessage.trim()) {
      return;
    }

    if (this.collectionCount === 0) {
      alert('Please index a repository first using the "Index Repository" tab');
      return;
    }

    // Add user message
    const userMessage: Message = {
      type: 'user',
      content: this.inputMessage,
      timestamp: new Date()
    };
    this.messages.push(userMessage);

    // Clear input
    const query = this.inputMessage;
    this.inputMessage = '';
    this.isLoading = true;

    // Query RAG system
    this.ragService.queryCodebase(query, 5).subscribe(
      (response: QueryResponse) => {
        const assistantMessage: Message = {
          type: 'assistant',
          content: response.answer,
          sources: response.sources,
          timestamp: new Date()
        };
        this.messages.push(assistantMessage);
        this.isLoading = false;
      },
      (error) => {
        const errorMessage: Message = {
          type: 'assistant',
          content: `Error: ${error.error?.detail || 'Failed to process query. Make sure Ollama is running.'}`,
          timestamp: new Date()
        };
        this.messages.push(errorMessage);
        this.isLoading = false;
      }
    );
  }

  loadCollectionStats() {
    this.ragService.getCollectionStats().subscribe(
      (stats) => {
        this.collectionCount = stats.count;
      },
      (error) => {
        console.error('Error loading collection stats:', error);
      }
    );
  }

  getSourceLabel(source: any): string {
    const name = source.filename || source.file_path;
    return `${name} (Lines ${source.start_line}-${source.end_line})`;
  }
}
