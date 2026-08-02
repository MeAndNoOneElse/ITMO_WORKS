import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SessionInfo } from '../../models/types';

@Component({
  selector: 'app-session-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './session-modal.html',
  styleUrls: ['./session-modal.css']
})
export class SessionModalComponent {
  @Input() visible: boolean = false;
  @Input() sessions: SessionInfo[] = [];
  @Output() close = new EventEmitter<void>();
  @Output() closeSessionEvent = new EventEmitter<number>();
  @Output() closeAllOthersEvent = new EventEmitter<void>();
  @Output() continueWithNewEvent = new EventEmitter<void>();

  formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    return date.toLocaleString();
  }

  closeSession(sessionId: number) {
    this.closeSessionEvent.emit(sessionId);
  }

  closeAllOthers() {
    this.closeAllOthersEvent.emit();
  }

  continueWithNew() {
    this.continueWithNewEvent.emit();
  }

  cancel() {
    this.close.emit();
  }
}

