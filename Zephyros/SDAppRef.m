//
//  SDAppClientProxy.m
//  Zephyros
//
//  Created by Steven Degutis on 8/12/13.
//  Copyright (c) 2013 Giant Robot Software. All rights reserved.
//

#import "SDAppRef.h"

#import "MACollectionUtilities.h"
#import "SDWindowRef.h"

#import "SDAppStalker.h"

@interface SDAppRef ()

@property id deathObserver;

@end

@implementation SDAppRef

- (void) whenDead:(void(^)())block {
    __weak SDAppRef* _self = self;
    self.deathObserver = [[NSNotificationCenter defaultCenter] addObserverForName:SDListenEventAppClosed
                                                                           object:nil
                                                                            queue:nil
                                                                       usingBlock:^(NSNotification *note) {
                                                                           if ([[[note userInfo] objectForKey:@"thing"] isEqual: _self.resource]) {
                                                                               [[NSNotificationCenter defaultCenter] removeObserver:_self.deathObserver];
                                                                               block();
                                                                           }
                                                                       }];
}

- (id) all_windows:(NSArray*)args msgID:(id)msgID {
    return MAP([self.resource allWindows], [self.client store: [SDWindowRef withResource: obj]]);
}

- (id) visible_windows:(NSArray*)args msgID:(id)msgID {
    return MAP([self.resource visibleWindows], [self.client store: [SDWindowRef withResource: obj]]);
}

- (id) title:(NSArray*)args msgID:(id)msgID {
    return [self.resource title];
}

- (id) hidden_q:(NSArray*)args msgID:(id)msgID {
    return @([self.resource isHidden]);
}

- (id) show:(NSArray*)args msgID:(id)msgID {
    [self.resource show];
    return [NSNull null];
}

- (id) hide:(NSArray*)args msgID:(id)msgID {
    [self.resource hide];
    return [NSNull null];
}

- (id) kill:(NSArray*)args msgID:(id)msgID {
    [self.resource kill];
    return [NSNull null];
}

- (id) kill9:(NSArray*)args msgID:(id)msgID {
    [self.resource kill9];
    return [NSNull null];
}

@end
