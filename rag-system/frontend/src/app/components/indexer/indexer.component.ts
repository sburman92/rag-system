import { Component, OnInit } from '@angular/core';
import { RagService } from '../../services/rag.service';

@Component({
  selector: 'app-indexer',
  templateUrl: './indexer.component.html',
  styleUrls: ['./indexer.component.css']
})
export class IndexerComponent implements OnInit {
  repoUrl = '';
  isIndexing = false;
  indexProgress = 0;
  indexMessage = '';
  lastIndexedRepo = '';
  collectionStats: any = null;

  constructor(private ragService: RagService) { }

  ngOnInit() {
    this.loadStats();
  }

  indexRepository() {
    if (!this.repoUrl.trim()) {
      alert('Please enter a GitHub repository URL');
      return;
    }

    this.isIndexing = true;
    this.indexProgress = 0;
    this.indexMessage = 'Starting indexing...';

    // Simulate progress
    const progressInterval = setInterval(() => {
      if (this.indexProgress < 90) {
        this.indexProgress += Math.random() * 30;
      }
    }, 500);

    this.ragService.indexRepository(this.repoUrl).subscribe(
      (response) => {
        clearInterval(progressInterval);
        this.indexProgress = 100;
        this.indexMessage = response.message;
        this.lastIndexedRepo = this.repoUrl;
        this.isIndexing = false;
        setTimeout(() => {
          this.loadStats();
        }, 1000);
      },
      (error) => {
        clearInterval(progressInterval);
        this.isIndexing = false;
        this.indexMessage = `Error: ${error.error?.detail || 'Indexing failed'}`;
      }
    );

    // Poll for status
    const statusInterval = setInterval(() => {
      if (!this.isIndexing) {
        clearInterval(statusInterval);
        return;
      }
      this.ragService.getIndexStatus().subscribe((status) => {
        this.indexProgress = status.progress;
        this.indexMessage = status.message;
      });
    }, 1000);
  }

  loadStats() {
    this.ragService.getCollectionStats().subscribe(
      (stats) => {
        this.collectionStats = stats;
      }
    );
  }

  clearVectorStore() {
    if (confirm('Are you sure you want to clear the vector store? This cannot be undone.')) {
      this.ragService.clearVectorStore().subscribe(
        () => {
          this.collectionStats = null;
          this.lastIndexedRepo = '';
          this.loadStats();
        }
      );
    }
  }
}
