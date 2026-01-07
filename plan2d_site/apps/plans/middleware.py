"""
Custom middleware to monitor and log plan visibility issues in production.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from apps.plans.models import Plan

logger = logging.getLogger('plans')


class PlanVisibilityMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to track plan visibility and alert on significant drops.
    Helps detect accidental filtering or visibility issues in production.
    """
    
    # Cache to avoid excessive database queries
    _last_count = None
    _check_interval = 0
    CHECK_FREQUENCY = 100  # Check every N requests
    
    def process_request(self, request):
        """Monitor plan visibility on certain pages."""
        # Only check on plan-related pages
        if not request.path.startswith('/plans/'):
            return None
        
        # Rate limit checks to avoid performance impact
        self.__class__._check_interval += 1
        if self.__class__._check_interval < self.CHECK_FREQUENCY:
            return None
        
        self.__class__._check_interval = 0
        
        # Get current visible plan count
        try:
            current_count = Plan.objects.visible().count()
            
            # First run - establish baseline
            if self.__class__._last_count is None:
                self.__class__._last_count = current_count
                logger.info(f"Plan visibility baseline: {current_count} visible plans")
                return None
            
            # Check for significant drops
            if current_count < self.__class__._last_count:
                drop = self.__class__._last_count - current_count
                drop_percentage = (drop / self.__class__._last_count) * 100 if self.__class__._last_count > 0 else 0
                
                if drop_percentage > 10:  # Alert on >10% drop
                    logger.warning(
                        f"⚠ Plan visibility drop detected! "
                        f"Was: {self.__class__._last_count}, Now: {current_count} "
                        f"({drop} plans, {drop_percentage:.1f}% decrease)"
                    )
                else:
                    logger.info(
                        f"Plan count changed: {self.__class__._last_count} → {current_count}"
                    )
                
                self.__class__._last_count = current_count
            elif current_count > self.__class__._last_count:
                added = current_count - self.__class__._last_count
                logger.info(f"✓ Plans added: +{added} (now {current_count} visible)")
                self.__class__._last_count = current_count
        
        except Exception as e:
            logger.error(f"Plan visibility monitoring error: {e}")
        
        return None
