import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RiskDisplay } from './risk-display';

describe('RiskDisplay', () => {
  let component: RiskDisplay;
  let fixture: ComponentFixture<RiskDisplay>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RiskDisplay]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RiskDisplay);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
