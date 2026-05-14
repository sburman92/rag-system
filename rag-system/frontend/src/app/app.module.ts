import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { ChatComponent } from './components/chat/chat.component';
import { IndexerComponent } from './components/indexer/indexer.component';
import { RagService } from './services/rag.service';

@NgModule({
  declarations: [
    AppComponent,
    ChatComponent,
    IndexerComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [RagService],
  bootstrap: [AppComponent]
})
export class AppModule { }
