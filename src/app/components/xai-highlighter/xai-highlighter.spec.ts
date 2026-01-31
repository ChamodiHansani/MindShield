import { ComponentFixture, TestBed } from '@angular/core/testing';

import { XaiHighlighter } from './xai-highlighter';

describe('XaiHighlighter', () => {
  let component: XaiHighlighter;
  let fixture: ComponentFixture<XaiHighlighter>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [XaiHighlighter]
    })
    .compileComponents();

    fixture = TestBed.createComponent(XaiHighlighter);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
